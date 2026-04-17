from app.core.config import logger
from app.core.celery_app import celery_app

from bertopic import BERTopic

bert_topic_model = None
MODEL_PATH = "models/bertopic_model"

def get_bert_model():
    global bert_topic_model
    if bert_topic_model is not None:
        return bert_topic_model

    try:
        # 1. Load the model without the heavy transformer
        model = BERTopic.load(MODEL_PATH, embedding_model=None)

        # 2. Safety check for set_params
        # Only set n_jobs if it's a real UMAP/Parametric model, 
        # not the 'BaseDimensionalityReduction' placeholder
        if hasattr(model, "umap_model"):
            # Check specifically if set_params exists on the instance
            set_params_func = getattr(model.umap_model, "set_params", None)
            if callable(set_params_func):
                model.umap_model.set_params(n_jobs=1)
                logger.info("UMAP n_jobs set to 1.")

        bert_topic_model = model
        return bert_topic_model

    except Exception as e:
        # This logger is vital to see exactly why it failed in Celery logs
        logger.error(f"Error loading model: {str(e)}")
        return None


@celery_app.task(
    queue="topic_queue",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3}
)
def topic_modelling(outputs):
    """
    Receives a LIST of contexts from the group of embed_text tasks.
    outputs = [ctx_year_1, ctx_year_2]
    """
    topic_model = get_bert_model()
    
    for ctx in outputs:
        if ctx.get("status") != "success":
            continue

        # Convert back to numpy for BERTopic
        import numpy as np
        embeddings = np.array(ctx["embeddings"])
        chunks = ctx["chunks"]

        # Perform Inference
        topics, probs = topic_model.transform(chunks, embeddings=embeddings)

        # Attach results
        ctx["topics"] = topics.tolist()
        ctx["topic_probs"] = probs.tolist() if probs is not None else []

        # del ctx["embeddings"]
        del ctx["chunks"]

    return outputs
