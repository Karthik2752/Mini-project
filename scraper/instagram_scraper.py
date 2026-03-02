# scraper/instagram_scraper.py

import requests

APIFY_TOKEN = "apify_api_ADTZEXQcJ33rDegIwfKrXsWwoskZIW2aNX7R"
ACTOR_ID = "apify/instagram-scraper"


def safe_get_nested(data, *keys):
    """Safely extract nested dictionary values"""
    for key in keys:
        if isinstance(data, dict) and key in data:
            data = data[key]
        else:
            return None
    return data


def scrape_instagram_post(post_url):

    url = f"https://api.apify.com/v2/acts/{ACTOR_ID}/run-sync-get-dataset-items?token={APIFY_TOKEN}"

    payload = {
        "directUrls": [post_url],
        "resultsLimit": 1,
        "resultsType": "posts"
    }

    response = requests.post(url, json=payload)

    if response.status_code != 200:
        print("Apify Error:", response.text)
        return None

    data = response.json()

    if not data:
        print("No Data Returned")
        return None

    item = data[0]

    print("DEBUG KEYS:", item.keys())

    # 🔥 PRODUCTION LEVEL EXTRACTION

    likes = (
        item.get("likesCount")
        or item.get("likeCount")
        or safe_get_nested(item, "edge_media_preview_like", "count")
        or 0
    )

    views = (
        item.get("videoViewCount")
        or item.get("videoPlayCount")
        or safe_get_nested(item, "video_view_count")
        or 0
    )

    comments_count = (
        item.get("commentsCount")
        or safe_get_nested(item, "edge_media_to_comment", "count")
        or 0
    )

    comments = []

    if "latestComments" in item:
        comments = [c.get("text", "") for c in item["latestComments"]]

    return {
        "likes": int(likes),
        "views": int(views),
        "comments_count": int(comments_count),
        "comments": comments
    }
