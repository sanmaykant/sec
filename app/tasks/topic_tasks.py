from app.core.config import logger
from app.core.celery_app import celery_app
from app.utils.load_model import get_bert_model
from app.utils.analysis import disappearing_risks, disappearing_with_drop

@celery_app.task(
    queue="topic_queue",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3}
)
def topic_modelling(outputs, target_year):
    """
    Receives a LIST of contexts from the group of embed_text tasks.
    outputs = [ctx_year_1, ctx_year_2]
    """
    topic_model = get_bert_model()
    if topic_model is None:
        raise Exception("Cannot load bertopic model")

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
        ctx["topics"] = topics.tolist() # pyright: ignore
        ctx["topic_probs"] = probs.tolist() if probs is not None else []

    logger.info("Analysis beginning")

    rel_years = list(filter(lambda ctx : ctx.get("year") != target_year, outputs))
    target_year = list(filter(lambda ctx : ctx.get("year") == target_year, outputs))[0]
    drs = []
    for ctx in rel_years:
        dr = disappearing_with_drop([ctx, target_year])
        drs.append(dr)

    ticker = target_year.get("ticker")

    logger.info("Analysis over")

    final_output = {
            "ticker": ticker,
            "analysis": list(zip(rel_years, drs)),
            "target_year": target_year,
            }

    return final_output
