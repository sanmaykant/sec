from app.core.celery_app import celery_app
from app.core.config import logger
from app.utils.analysis import disappearing_risks

@celery_app.task(
    queue="analysis_queue",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3}
)
def disappearing_analysis(outputs):
    logger.info("Analysis beginning")

    ticker = outputs[0].get("ticker")
    year1 = min(outputs[0].get("year"), outputs[1].get("year"))
    year2 = max(outputs[0].get("year"), outputs[1].get("year"))

    dr = disappearing_risks(ticker, year1, year2, outputs)
    logger.info("Analysis over")
    logger.info(dr)

    return dr
