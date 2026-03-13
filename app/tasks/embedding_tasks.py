from app.core.config import logger
from app.core.celery_app import celery_app
from sentence_transformers import SentenceTransformer
from app.utils.preprocessing import preprocess_risk_section


import os
os.environ["HF_HUB_OFFLINE"] = "1"

model = SentenceTransformer(
        "sentence-transformers/all-mpnet-base-v2",
        revision="e8c3b32edf5434bc2275fc9bab85f82640a19130",
        local_files_only=True)

@celery_app.task(
    queue="embed_queue",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3}
)
def embed_text(ctx):
    if ctx.get("status") != "success":
        return ctx

    logger.info("Processing text")
    sentences = preprocess_risk_section(ctx["filing"], model)
    if not sentences:
        return { "embeddings": [] }

    logger.info("Embedding text")
    # sentences = [ctx["filing"]]
    embeddings = model.encode(sentences, convert_to_tensor=True, batch_size=64)
    logger.info(f"Embedded text {embeddings}")

    return {
        "embeddings": ctx["filing"],
    }
