from app.core.config import logger
from app.core.celery_app import celery_app
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')


@celery_app.task(
    queue="extract_queue",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3}
)
def extract_section(fetch_result):
    if fetch_result.get("status") != "success":
        return fetch_result

    logger.info("Embedding text")

    sentences = ["Hi, I am a sentence!", "Hi, I am another sentence!"]
    embeddings = model.encode(sentences, convert_to_tensor=True, batch_size=256)

    logger.info(f"Embedded text {embeddings}")

    return {
        "extracted": fetch_result["filing"],
    }
