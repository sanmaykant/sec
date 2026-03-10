import time
from app.core.celery_app import celery_app
from app.services.edgar_service import EdgarService

from edgar import Company, set_identity

service = EdgarService()


@celery_app.task(
    queue="fetch_queue",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3}
)
def fetch_filing(job_id: str, ticker: str, year: int, form: str):
    set_identity("your.name@example.com")

    x = Company(ticker)
    filing = x.get_filings(form=form, year=year)[0]

    return {
        "year": year,
        "ticker": ticker,
        "status": "success",
        "filing": filing.accession_number
    }
