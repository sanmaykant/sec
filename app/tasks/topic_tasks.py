from app.core.config import logger
from app.core.celery_app import celery_app
from app.utils.load_model import get_bert_model, get_topic_data
from app.utils.analysis import disappearing_risks, disappearing_with_drop

def get_topic_objects(topic_ids):
    topic_data = get_topic_data()
    if topic_data is None:
        return []

    topic_map = dict(zip(topic_data['Topic'], topic_data['Name']))

    return [
            {"topic": topic[0], "name": topic_map.get(topic[0], "Unknown Topic"), "freq1": topic[1], "freq2": topic[2]} 
        for topic in topic_ids
    ]

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

    topic_data = get_topic_data()
    if topic_data is None:
        raise Exception("Topic data not found")

    rel_years = list(filter(lambda ctx : ctx.get("year") != target_year, outputs))
    target_year = list(filter(lambda ctx : ctx.get("year") == target_year, outputs))[0]
    drs = []
    for ctx in rel_years:
        dr = disappearing_with_drop([ctx, target_year])
        topic_id_name_map = get_topic_objects(dr)
        drs.append(topic_id_name_map)

    ticker = target_year.get("ticker")

    logger.info("Analysis over")

    final_output = {
            "ticker": ticker,
            "analysis": list(zip(rel_years, drs)),
            "target_year": target_year,
            }

    return final_output

def get_topic_objectss(topic_ids):
    topic_data = get_topic_data()
    if topic_data is None:
        return []

    topic_map = dict(zip(topic_data['Topic'], topic_data['Name']))

    return [
        {"topic": topic, "name": topic_map.get(topic, "Unknown Topic")} 
        for topic in topic_ids
    ]

@celery_app.task(
    queue="topic_queue",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3}
)
def topic_modellingg(outputs, target_year):
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

    topic_data = get_topic_data()
    if topic_data is None:
        raise Exception("Topic data not found")

    rel_years = list(filter(lambda ctx : ctx.get("year") != target_year, outputs))
    target_year = list(filter(lambda ctx : ctx.get("year") == target_year, outputs))[0]
    drs = []
    for ctx in rel_years:
        dr = disappearing_risks([ctx, target_year])
        topic_id_name_map = get_topic_objectss(dr)
        drs.append(topic_id_name_map)

    ticker = target_year.get("ticker")

    logger.info("Analysis over")

    final_output = {
            "ticker": ticker,
            "analysis": list(zip(rel_years, drs)),
            "target_year": target_year,
            }

    return final_output
