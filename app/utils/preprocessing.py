from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import util
from collections import Counter
import numpy as np
import re
from collections import defaultdict
from tqdm import tqdm


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




def preprocess_text(text):
    text = re.sub(r"<.*?>", " ", text)  # remove HTML
    text = text.replace("\r\n", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()

def chunk_text(text, min_length=100, max_length=800):
    paragraphs = re.split(r"\n{2,}", text)

    chunks = []
    buffer = ""

    for p in paragraphs:
        p = p.strip()
        if not p:
            continue

        if len(buffer) + len(p) < max_length:
            buffer += " " + p
        else:
            if len(buffer) > min_length:
                chunks.append(buffer.strip())
            buffer = p

    if len(buffer) > min_length:
        chunks.append(buffer.strip())

    return chunks

def prepare_chunks_with_metadata(results):
    all_chunks = []
    metadata = []

    year_chunks = defaultdict(list)
    company_chunks = defaultdict(list)

    for item in tqdm(results):
        ticker = item["ticker"]
        year = item["year"]

        text = preprocess_text(item["filing"])
        chunks = chunk_text(text)

        for chunk in chunks:
            all_chunks.append(chunk)

            metadata.append({
                "ticker": ticker,
                "year": year
            })

            year_chunks[year].append(chunk)
            company_chunks[ticker].append(chunk)

    return {
        "all_chunks": all_chunks,
        "metadata": metadata,
        "year_chunks": dict(year_chunks),
        "company_chunks": dict(company_chunks)
    }
