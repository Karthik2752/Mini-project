# scraper/instagram_scraper.py

import requests
import os

# 🔐 Better: store token in environment variable
APIFY_TOKEN = os.getenv("apify_api_Rp6wePfMrR8E7hUeaOz8l9Q9uhIWax2QRO8I")  # Set in system or .env file

def scrape_instagram_post(post_url):
    """
    Fetch Instagram post data using Apify API
    """

    if not APIFY_TOKEN:
        return {
            "caption": "Missing Apify Token",
            "likes": 0,
            "views": 0,
            "comments": []
        }

    api_url = f"https://api.apify.com/v2/acts/apify~instagram-post-scraper/run-sync-get-dataset-items?token={APIFY_TOKEN}"

    payload = {
        "directUrls": [post_url],
        "resultsLimit": 1
    }

    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()

        data = response.json()

        if not data:
            return {
                "caption": "No data found",
                "likes": 0,
                "views": 0,
                "comments": []
            }

        post = data[0]

        caption = post.get("caption", "")
        likes = post.get("likesCount", 0)
        views = post.get("videoViewCount", 0)

        # Extract comments safely
        comments_data = post.get("comments", [])
        comments = []

        for comment in comments_data:
            text = comment.get("text")
            if text:
                comments.append(text)

        return {
            "caption": caption,
            "likes": likes,
            "views": views,
            "comments": comments
        }

    except requests.exceptions.RequestException as e:
        return {
            "caption": f"API Error: {str(e)}",
            "likes": 0,
            "views": 0,
            "comments": []
        }