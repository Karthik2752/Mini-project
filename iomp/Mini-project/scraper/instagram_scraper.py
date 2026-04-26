import json
import os
import random
import re
from typing import Any, Dict, List, Optional, Tuple

from bs4 import BeautifulSoup


def is_valid_instagram_url(url: str) -> bool:
    pattern = r"^https?://(www\.)?instagram\.com/(reel|p)/[A-Za-z0-9_\-]+/?"
    return bool(re.match(pattern, url))


def _safe_get(data: Any, *keys: str) -> Any:
    for key in keys:
        if isinstance(data, dict) and key in data:
            data = data[key]
        else:
            return None
    return data


def _to_int(value: Any) -> int:
    try:
        if value is None:
            return 0
        if isinstance(value, str):
            value = value.replace(",", "").strip()
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def _parse_short_number(value: str) -> int:
    text = (value or "").strip().lower().replace(",", "")
    match = re.match(r"^(\d+(\.\d+)?)([kmb])?$", text)
    if not match:
        return _to_int(text)
    number = float(match.group(1))
    suffix = match.group(3)
    if suffix == "k":
        number *= 1_000
    elif suffix == "m":
        number *= 1_000_000
    elif suffix == "b":
        number *= 1_000_000_000
    return int(number)


def _humanize(value: int) -> str:
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"{value / 1_000:.1f}K"
    return str(value)


def _clean_instagram_url(url: str) -> str:
    # Remove query params like ?igsh=...
    return url.split("?")[0].rstrip("/") + "/"


def _extract_shortcode(url: str) -> Optional[str]:
    match = re.search(r"instagram\.com/(reel|p)/([A-Za-z0-9_\-]+)/?", url)
    return match.group(2) if match else None


def _extract_comments(item: Dict[str, Any]) -> List[str]:
    comments: List[str] = []
    candidates = (
        item.get("latestComments")
        or item.get("comments")
        or _safe_get(item, "edge_media_to_parent_comment", "edges")
        or []
    )

    if isinstance(candidates, list):
        for obj in candidates:
            if isinstance(obj, str):
                if obj.strip():
                    comments.append(obj.strip())
                continue
            text = (
                obj.get("text")
                or _safe_get(obj, "node", "text")
                or _safe_get(obj, "comment", "text")
                or ""
            )
            if text and isinstance(text, str):
                comments.append(text.strip())
    return comments


def _normalize_item(item: Dict[str, Any], source: str = "instaloader") -> Dict[str, Any]:
    likes = _to_int(
        item.get("likesCount")
        or item.get("likeCount")
        or _safe_get(item, "edge_media_preview_like", "count")
        or _safe_get(item, "owner", "edge_owner_to_timeline_media", "count")
    )
    views = _to_int(
        item.get("videoViewCount")
        or item.get("videoPlayCount")
        or item.get("playsCount")
        or _safe_get(item, "video_view_count")
        or _safe_get(item, "video", "play_count")
    )
    comments_count = _to_int(
        item.get("commentsCount")
        or item.get("commentCount")
        or _safe_get(item, "edge_media_to_comment", "count")
    )
    comments = _extract_comments(item)
    caption = item.get("caption") or _safe_get(item, "edge_media_to_caption", "edges") or ""
    if isinstance(caption, list):
        caption = _safe_get(caption[0], "node", "text") if caption else ""

    return {
        "likes": likes,
        "views": views,
        "comments_count": comments_count,
        "comments": comments,
        "caption": caption if isinstance(caption, str) else "",
        "likes_display": _humanize(likes),
        "views_display": _humanize(views),
        "comments_count_display": _humanize(comments_count),
        "is_estimated": source in {"demo", "playwright"},
        "source": source,
        "comments_source": "unknown",
    }


def _extract_counts_from_og_description(text: str) -> Tuple[int, int]:
    """
    Instagram og:description often looks like:
      '12,345 likes, 678 comments - ...'
    Returns (likes, comments_count)
    """
    if not text:
        return 0, 0
    likes = 0
    comments = 0
    like_match = re.search(r"([\d,.]+)\s+likes?", text, flags=re.IGNORECASE)
    comment_match = re.search(r"([\d,.]+)\s+comments?", text, flags=re.IGNORECASE)
    if like_match:
        likes = _to_int(like_match.group(1))
    if comment_match:
        comments = _to_int(comment_match.group(1))
    return likes, comments


def _try_instaloader(post_url: str) -> Optional[Dict[str, Any]]:
    shortcode = _extract_shortcode(post_url)
    if not shortcode:
        return None

    try:
        import instaloader  # type: ignore
    except Exception:
        return None

    username = os.getenv("INSTA_USERNAME", "").strip()
    password = os.getenv("INSTA_PASSWORD", "").strip()
    session_file = os.getenv("INSTA_SESSION_FILE", "insta_session")

    loader = instaloader.Instaloader(
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False,
        quiet=True,
    )

    # Best reliability: reuse session, otherwise login if creds exist.
    try:
        if os.path.exists(session_file):
            loader.load_session_from_file(username or None, filename=session_file)
        elif username and password:
            loader.login(username, password)
            loader.save_session_to_file(filename=session_file)
    except Exception:
        # Continue without session (may work for some public posts)
        pass

    try:
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
    except Exception:
        return None

    likes = _to_int(getattr(post, "likes", 0))
    comments_count = _to_int(getattr(post, "comments", 0))
    caption = getattr(post, "caption", "") or ""

    views = 0
    try:
        views = _to_int(getattr(post, "video_view_count", 0) or 0)
    except Exception:
        views = 0

    comments_list: List[str] = []
    try:
        # Limit to avoid slow scraping
        for i, c in enumerate(post.get_comments()):
            if i >= 50:
                break
            text = getattr(c, "text", "") or ""
            if text.strip():
                comments_list.append(text.strip())
    except Exception:
        comments_list = []

    item = {
        "likesCount": likes,
        "videoViewCount": views,
        "commentsCount": comments_count,
        "latestComments": [{"text": t} for t in comments_list],
        "caption": caption,
    }
    normalized = _normalize_item(item, source="instaloader")
    normalized["comments_source"] = "scraped" if comments_list else "unavailable"
    if normalized["likes"] == 0 and normalized["views"] == 0 and normalized["comments_count"] == 0:
        return None
    return normalized


def _try_playwright(post_url: str) -> Optional[Dict[str, Any]]:
    """
    Public-page fallback (works without credentials sometimes, but can still be blocked).
    """
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except Exception:
        return None

    cleaned = _clean_instagram_url(post_url)
    html = ""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0.0.0 Safari/537.36"
                )
            )
            page = context.new_page()
            page.goto(cleaned, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(2500)
            html = page.content()
            context.close()
            browser.close()
    except Exception:
        return None

    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")
    og_desc = ""
    og = soup.find("meta", attrs={"property": "og:description"})
    if og and og.get("content"):
        og_desc = og["content"]

    likes, comments_count = _extract_counts_from_og_description(og_desc)
    caption = ""
    title = soup.find("meta", attrs={"property": "og:title"})
    if title and title.get("content"):
        caption = title["content"]

    # Try to parse embedded JSON (best-effort)
    views = 0
    extracted_comments: List[str] = []
    try:
        for script in soup.find_all("script"):
            if script.string and "video_view_count" in script.string:
                m = re.search(r"\"video_view_count\"\s*:\s*(\d+)", script.string)
                if m:
                    views = _to_int(m.group(1))
                    break
    except Exception:
        views = 0

    # Best-effort comment text extraction from embedded JSON blobs
    try:
        for script in soup.find_all("script"):
            if not script.string:
                continue
            s = script.string
            if "\"edge_media_to_parent_comment\"" not in s and "\"comment\"" not in s:
                continue
            # Extract `"text":"..."`
            for m in re.finditer(r"\"text\"\s*:\s*\"((?:\\\"|[^\"])*)\"", s):
                raw = m.group(1)
                text = bytes(raw, "utf-8").decode("unicode_escape").replace("\\/", "/")
                text = text.strip()
                if 2 < len(text) < 300:
                    extracted_comments.append(text)
            if len(extracted_comments) >= 80:
                break
    except Exception:
        extracted_comments = []

    # De-duplicate while preserving order
    deduped: List[str] = []
    seen = set()
    for c in extracted_comments:
        if c not in seen:
            seen.add(c)
            deduped.append(c)

    item = {
        "likesCount": likes,
        "videoViewCount": views,
        "commentsCount": comments_count,
        "latestComments": [{"text": t} for t in deduped[:50]],
        "caption": caption,
    }
    normalized = _normalize_item(item, source="playwright")
    if normalized["comments"]:
        normalized["comments_source"] = "scraped_limited"
    else:
        normalized["comments_source"] = "synthetic_sample"
        normalized["comments"] = [
            "Great reel!",
            "Nice content.",
            "Could be improved with better audio.",
            "Hook can be stronger.",
            "Very informative.",
        ]
    if normalized["likes"] == 0 and normalized["views"] == 0 and normalized["comments_count"] == 0:
        return None
    return normalized


def _demo_data(post_url: str, reason: str) -> Dict[str, Any]:
    sample_comments = [
        "Amazing reel, very helpful.",
        "Loved the editing and transitions.",
        "Audio could be better.",
        "I stayed till the end, great pacing.",
        "Not clear in the first few seconds.",
        "Super useful tips, thanks!",
    ]
    item = {
        "likesCount": random.randint(1200, 54000),
        "videoViewCount": random.randint(6000, 240000),
        "commentsCount": random.randint(20, 900),
        "latestComments": [{"text": c} for c in sample_comments],
        "caption": f"Demo fallback for {post_url}. Reason: {reason}",
    }
    normalized = _normalize_item(item, source="demo")
    normalized["comments_source"] = "synthetic_sample"
    return normalized


def scrape_instagram_reel(post_url: str) -> Dict[str, Any]:
    if not is_valid_instagram_url(post_url):
        return _demo_data(post_url, "Invalid Instagram URL")

    cleaned = _clean_instagram_url(post_url)

    instaloader_data = _try_instaloader(cleaned)
    if instaloader_data:
        return instaloader_data

    playwright_data = _try_playwright(cleaned)
    if playwright_data:
        return playwright_data

    return _demo_data(cleaned, "All scraping methods failed (likely private/login wall)")
