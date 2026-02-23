# analysis/sentiment_analysis.py

from textblob import TextBlob

def analyze_sentiment(comments):
    """
    Analyze sentiment of Instagram comments
    Returns count of positive, negative and neutral comments
    """

    positive = 0
    negative = 0
    neutral = 0

    for comment in comments:
        analysis = TextBlob(comment)
        polarity = analysis.sentiment.polarity

        if polarity > 0:
            positive += 1
        elif polarity < 0:
            negative += 1
        else:
            neutral += 1

    total = len(comments)

    return {
        "positive": positive,
        "negative": negative,
        "neutral": neutral,
        "total_comments": total
    }