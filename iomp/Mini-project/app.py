from datetime import datetime
from flask import Flask, jsonify, render_template, request

from analysis.keyword_extraction import extract_keywords
from analysis.retention_analysis import calculate_retention
from analysis.suggestion_engine import generate_strategy_report
from database import get_reports, save_report
from scraper.instagram_scraper import is_valid_instagram_url, scrape_instagram_reel

app = Flask(__name__)

def _pct(numer: float, denom: float) -> float:
    if not denom:
        return 0.0
    return round((numer / denom) * 100, 2)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    post_url = (request.form.get("post_url") or "").strip()
    if not post_url:
        return render_template("dashboard.html", error="Please provide an Instagram Reel URL.")

    if not is_valid_instagram_url(post_url):
        return render_template(
            "dashboard.html",
            error="Invalid URL. Please enter a valid Instagram reel URL.",
        )

    scraped = scrape_instagram_reel(post_url)

    likes = scraped.get("likes", 0)
    views = scraped.get("views", 0)
    comments_count = scraped.get("comments_count", 0)
    caption = scraped.get("caption", "")

    # Comments scraping is unreliable on Instagram; analyze using caption/title instead.
    keywords = extract_keywords([caption] if caption else [])
    retention_score, retention_level = calculate_retention(likes, views)

    like_rate = _pct(likes, views)                 # likes / views
    comment_rate = _pct(comments_count, views)     # comments / views
    engagement_rate = _pct(likes + comments_count, views)  # (likes+comments)/views
    interaction_ratio = _pct(comments_count, likes)        # comments / likes

    strategy = generate_strategy_report(
        likes=likes,
        views=views,
        comments=comments_count,
        like_rate=like_rate,
        comment_rate=comment_rate,
        engagement_rate=engagement_rate,
        interaction_ratio=interaction_ratio,
        keywords=keywords,
    )

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result = {
        "post_url": post_url,
        "likes": likes,
        "views": views,
        "comments_count": comments_count,
        "likes_display": scraped.get("likes_display", "0"),
        "views_display": scraped.get("views_display", "0"),
        "comments_count_display": scraped.get("comments_count_display", "0"),
        "caption": caption or "No caption available.",
        "retention_score": retention_score,
        "retention_level": retention_level,
        "keywords": keywords,
        "performance": strategy["performance"],
        "reason": strategy["reason"],
        "suggestions": strategy["suggestions"],
        "like_rate": like_rate,
        "comment_rate": comment_rate,
        "engagement_rate": engagement_rate,
        "interaction_ratio": interaction_ratio,
        "timestamp": timestamp,
        "source": scraped.get("source", "unknown"),
        "is_estimated": scraped.get("is_estimated", False),
    }
    save_report(result)
    return render_template("dashboard.html", result=result)


@app.route("/history")
def history():
    reports = list(reversed(get_reports()))
    return render_template("history.html", reports=reports)


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True)
