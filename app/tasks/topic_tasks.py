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
def topic_modelling(outputs):
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

        # del ctx["embeddings"]
        # del ctx["chunks"]

    logger.info("Analysis beginning")

    ticker = outputs[0].get("ticker")
    year1 = min(outputs[0].get("year"), outputs[1].get("year"))
    year2 = max(outputs[0].get("year"), outputs[1].get("year"))

    year1_out = list(filter(lambda ctx : ctx.get("year") == year1, outputs))[0]
    year2_out = list(filter(lambda ctx : ctx.get("year") == year2, outputs))[0]

    # dr = disappearing_risks(outputs)
    dr = disappearing_with_drop(outputs)
    logger.info("Analysis over")
    logger.info(dr)

    final_output = {
            "ticker": ticker,
            "analysis": [year1_out, year2_out],
            "dr": dr
            }

    return final_output
