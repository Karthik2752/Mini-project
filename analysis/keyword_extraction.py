# analysis/keyword_extraction.py

from sklearn.feature_extraction.text import CountVectorizer
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os
import re

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    return text


def extract_keywords(comments):
    if not comments:
        return [], None

    cleaned_comments = [clean_text(c) for c in comments if len(c) > 3]

    vectorizer = CountVectorizer(stop_words='english')
    X = vectorizer.fit_transform(cleaned_comments)

    word_counts = X.sum(axis=0)
    words_freq = [
        (word, word_counts[0, idx])
        for word, idx in vectorizer.vocabulary_.items()
    ]

    sorted_words = sorted(words_freq, key=lambda x: x[1], reverse=True)

    top_keywords = sorted_words[:10]

    # Generate WordCloud
    wordcloud = WordCloud(width=600, height=400, background_color='white')
    wordcloud.generate_from_frequencies(dict(top_keywords))

    image_path = "static/images/wordcloud.png"
    wordcloud.to_file(image_path)

    return top_keywords, image_path