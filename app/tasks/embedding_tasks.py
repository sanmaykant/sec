from app.core.config import logger
from app.core.celery_app import celery_app
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer(
        "sentence-transformers/all-mpnet-base-v2",
        revision="e8c3b32edf5434bc2275fc9bab85f82640a19130",
        local_files_only=True)

import os
os.environ["HF_HUB_OFFLINE"] = "1"


@celery_app.task(
    queue="embed_queue",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3}
)
def embed_text(fetch_result):
    if fetch_result.get("status") != "success":
        return fetch_result

    logger.info("Embedding text")

    sentences = [fetch_result["filing"]]
    embeddings = model.encode(sentences, convert_to_tensor=True, batch_size=256)

    logger.info(f"Embedded text {embeddings}")

    return {
        "embedding": fetch_result["filing"],
    }
