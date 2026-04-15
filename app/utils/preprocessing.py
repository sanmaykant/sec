from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import util
from collections import Counter
import numpy as np
import re

def remove_high_frequency_sentences(sentences, threshold=0.05):
    # Remove sentences that appear very frequently within the text (frequency > threshold)
    counts = Counter(sentences)
    total = len(sentences)
    filtered = [s for s in sentences if counts[s]/total < threshold]
    return filtered

def remove_low_tfidf_sentences(sentences, top_fraction=0.7):
    # Keep only sentences with high TF-IDF scores
    if len(sentences) <= 1:
        return sentences
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(sentences)
    sentence_scores = X.sum(axis=1).A1  # Sum TF-IDF of all words in sentence
    threshold = np.percentile(sentence_scores, (1-top_fraction)*100)
    filtered = [s for i, s in enumerate(sentences) if sentence_scores[i] >= threshold]
    return filtered

def preprocess_risk_section(text, model):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 0]

    sentences = remove_high_frequency_sentences(sentences, threshold=0.05)

    sentences = remove_low_tfidf_sentences(sentences, top_fraction=0.7)

    return sentences
