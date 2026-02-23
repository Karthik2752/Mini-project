# app.py

from flask import Flask, render_template, request
from scraper.instagram_scraper import scrape_instagram_post
from analysis.sentiment_analysis import analyze_sentiment
import json
import os
from datetime import datetime

app = Flask(__name__)

DATABASE_FILE = "analysis_history.json"


# ---------- DATABASE FUNCTION ----------
def save_to_database(data):
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, "r") as file:
            history = json.load(file)
    else:
        history = []

    history.append(data)

    with open(DATABASE_FILE, "w") as file:
        json.dump(history, file, indent=4)


# ---------- ROUTES ----------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    post_url = request.form["post_url"]

    # Scrape data
    scraped_data = scrape_instagram_post(post_url)

    # Sentiment analysis
    sentiment_result = analyze_sentiment(scraped_data["comments"])

    # Retention Score (Simple Formula)
    likes = scraped_data["likes"]
    views = scraped_data["views"]

    if views > 0:
        retention_score = round((likes / views) * 100, 2)
    else:
        retention_score = 0

    # Prepare result
    result = {
        "url": post_url,
        "caption": scraped_data["caption"],
        "likes": likes,
        "views": views,
        "sentiment": sentiment_result,
        "retention_score": retention_score,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Save to JSON database
    save_to_database(result)

    return render_template("dashboard.html", result=result)


@app.route("/history")
def history():
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, "r") as file:
            history_data = json.load(file)
    else:
        history_data = []

    return render_template("history.html", history=history_data)


# ---------- MAIN ----------

if __name__ == "__main__":
    app.run(debug=True)