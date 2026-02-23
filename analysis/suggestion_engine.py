# analysis/suggestion_engine.py

def generate_suggestions(retention_level, positive, negative, neutral, keywords):

    suggestions = []

    # 1️⃣ Retention Based Suggestions
    if retention_level == "Low":
        suggestions.append("Improve the first 3 seconds hook to grab attention.")
        suggestions.append("Use faster editing and engaging visuals.")
        suggestions.append("Add captions or subtitles to retain viewers.")

    elif retention_level == "Medium":
        suggestions.append("Try adding a stronger call-to-action.")
        suggestions.append("Improve storytelling to increase watch time.")

    else:
        suggestions.append("Great retention! Maintain similar content style.")

    # 2️⃣ Sentiment Based Suggestions
    if negative > positive:
        suggestions.append("Audience feedback is mostly negative. Improve content quality.")
        suggestions.append("Address common complaints in next post.")

    if positive > negative:
        suggestions.append("Positive audience response. Create similar content.")

    # 3️⃣ Keyword Based Suggestions
    keyword_words = [word for word, count in keywords]

    if "boring" in keyword_words:
        suggestions.append("Content feels boring. Add more dynamic elements.")

    if "audio" in keyword_words:
        suggestions.append("Improve audio clarity and background music.")

    if "quality" in keyword_words:
        suggestions.append("Upgrade video resolution and editing quality.")

    if not suggestions:
        suggestions.append("Content performance is stable. Try experimenting with new trends.")

    return suggestions