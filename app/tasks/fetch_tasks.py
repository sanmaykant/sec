import time
from app.core.celery_app import celery_app
from app.services.edgar_service import EdgarService

service = EdgarService()


@celery_app.task(
    queue="fetch_queue",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3}
)
def fetch_filing(ticker: str, year: int):
    time.sleep(2)
    return {
        "year": year,
        "ticker": ticker,
        "status": "success",
    }
