import gc
import torch

from app.core.config import logger
from app.core.celery_app import celery_app
from sentence_transformers import SentenceTransformer
from app.utils.preprocessing import preprocess_text, chunk_text


import os
os.environ["HF_HUB_OFFLINE"] = "1"

model = SentenceTransformer(
        "sentence-transformers/all-mpnet-base-v2",
        revision="e8c3b32edf5434bc2275fc9bab85f82640a19130",
        local_files_only=True, device="cuda")

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

    text = preprocess_text(ctx["filing"])
    chunks = chunk_text(text)

    if not chunks:
        return { "embeddings": [] }

    logger.info("Embedding text")
    embeddings = model.encode(chunks, convert_to_tensor=True, batch_size=32)
    logger.info(f"Embedded text {embeddings}")

    ctx["embeddings"] = embeddings.tolist()
    ctx["chunks"] = chunks

# Explicitly cleanup
    del embeddings 
    gc.collect() # Trigger Python garbage collection
    if torch.cuda.is_available():
        torch.cuda.empty_cache() # Release unused VRAM back to the GPU

    return ctx
