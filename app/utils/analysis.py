from app.utils.load_model import get_bert_model
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter


def max_similarity(topic_id, other_topic_ids, topic_embeddings):
    if not other_topic_ids:
        return 0

    sims = cosine_similarity(
        topic_embeddings[topic_id].reshape(1, -1),
        topic_embeddings[other_topic_ids]
    )

    return sims.max()

def get_topics(ticker, year, docs):
    return set([
        item["topics"]
        for item in docs
        if item["ticker"] == ticker
        and item["year"] == year
        and item["topics"] != -1
    ])

def disappearing_risks(docs, threshold=1):
    topics_1 = set(docs[0].get("topics") if docs[0].get("year") < docs[1].get("year") else docs[1].get("topics"))
    topics_2 = set(docs[0].get("topics") if docs[0].get("year") > docs[1].get("year") else docs[1].get("topics"))

    topic_model = get_bert_model()
    if topic_model is None:
        raise Exception("Cannot load bertopic")
    topic_embeddings = topic_model.topic_embeddings_

    disappearing = []

    for t1 in topics_1:
        sim = max_similarity(t1, list(topics_2), topic_embeddings)

        if sim < threshold:
            disappearing.append(t1)

    return disappearing

def disappearing_with_drop(docs, drop_ratio=0.7):
    topics_1 = docs[0].get("topics") if docs[0].get("year") < docs[1].get("year") else docs[1].get("topics")
    topics_2 = docs[0].get("topics") if docs[0].get("year") > docs[1].get("year") else docs[1].get("topics")

    counts1 = Counter(topics_1)
    counts2 = Counter(topics_2)

    disappearing = []

    for topic in counts1:
        freq1 = counts1[topic]
        freq2 = counts2.get(topic, 0)

        if freq2 < freq1 * drop_ratio:
            disappearing.append((topic, freq1, freq2))

    return disappearing
