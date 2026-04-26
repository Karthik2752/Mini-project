import re
from collections import Counter

STOP_WORDS = {
    "the",
    "is",
    "and",
    "to",
    "a",
    "of",
    "it",
    "for",
    "in",
    "on",
    "this",
    "that",
    "with",
    "you",
    "your",
    "was",
    "are",
    "very",
    "just",
    "but",
    "have",
    "not",
    "from",
    "they",
    "what",
    "about",
    "can",
    "all",
    "our",
    "too",
}

def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    return text


def extract_keywords(comments, top_n=10):
    if not comments:
        return []

    cleaned = [clean_text(c) for c in comments if isinstance(c, str) and c.strip()]
    words = []
    for sentence in cleaned:
        for word in sentence.split():
            if len(word) > 2 and word not in STOP_WORDS:
                words.append(word)

    counts = Counter(words)
    return counts.most_common(top_n)