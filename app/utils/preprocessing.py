from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import util
from collections import Counter
import numpy as np
import re

# Initial regex patterns
BOILERPLATE_PATTERNS = [
    r"forward[- ]looking statements",
    r"the company (?:believes|may|will|can|could|should)",
    r"risks and uncertainties",
    r"this (?:report|filing)",
    r"uncertainties inherent in",
    r"the following risk factors",
    r"our business is subject to various risks",
    r"may adversely affect our business",
]

# Example known boilerplate sentences from prior filings
KNOWN_BOILERPLATE = [
    "we are subject to various risks and uncertainties",
    "our business may be affected by general economic conditions",
    "forward-looking statements involve known and unknown risks"
]

def remove_regex_boilerplate(text):
    text = text.lower()
    for pattern in BOILERPLATE_PATTERNS:
        text = re.sub(pattern, "", text)
    return text

def remove_high_frequency_sentences(sentences, threshold=0.05):
    """
    Remove sentences that appear very frequently within the text (frequency > threshold)
    """
    counts = Counter(sentences)
    total = len(sentences)
    filtered = [s for s in sentences if counts[s]/total < threshold]
    return filtered

def remove_low_tfidf_sentences(sentences, top_fraction=0.7):
    """
    Keep only sentences with high TF-IDF scores
    """
    if len(sentences) <= 1:
        return sentences
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(sentences)
    sentence_scores = X.sum(axis=1).A1  # Sum TF-IDF of all words in sentence
    threshold = np.percentile(sentence_scores, (1-top_fraction)*100)
    filtered = [s for i, s in enumerate(sentences) if sentence_scores[i] >= threshold]
    return filtered

def remove_embedding_similar_boilerplate(sentences, known_boilerplate, model, similarity_threshold=0.85):
    """
    Remove sentences that are semantically very similar to known boilerplate
    """
    if not known_boilerplate or not sentences:
        return sentences
    emb_sentences = model.encode(sentences, convert_to_tensor=True, batch_size=32)
    emb_boilerplate = model.encode(known_boilerplate, convert_to_tensor=True, batch_size=32)
    filtered = []
    for i, s_emb in enumerate(emb_sentences):
        sims = util.cos_sim(s_emb, emb_boilerplate)
        if sims.max() < similarity_threshold:
            filtered.append(sentences[i])
    return filtered

def preprocess_risk_section(text, model):
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 0]

    # 1. Regex boilerplate removal
    text_clean = remove_regex_boilerplate(" ".join(sentences))
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text_clean) if s.strip()]

    # 2. High-frequency sentence removal
    sentences = remove_high_frequency_sentences(sentences, threshold=0.05)

    # 3. Low-TF-IDF sentence removal
    sentences = remove_low_tfidf_sentences(sentences, top_fraction=0.7)

    # 4. Embedding-based known boilerplate removal
    sentences = remove_embedding_similar_boilerplate(sentences, KNOWN_BOILERPLATE, model, similarity_threshold=0.85)

    return sentences
