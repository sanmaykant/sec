import time
from typing import Dict, Any

from edgar import Company, set_identity
from edgar.entity import EntityFiling

from celery.exceptions import Ignore

from app.core.celery_app import celery_app
from app.services.edgar_service import EdgarService


def skip(job_id: str, year: int, ticker: str):
    return {
        "status": "skip",
        "reason": "filing_not_found",
        "job_id": job_id,
        "year": year,
        "ticker": ticker
        }

@celery_app.task(
    queue="fetch_queue",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3}
)
def fetch_filing(
        job_id: str,
        ticker: str,
        year: int,
        form: str,
        section_name: str):

    service = EdgarService()
    set_identity("your.name@example.com")

    x = Company(ticker)
    filings = x.get_filings(form=form, year=year)

    if len(filings) == 0:
        return skip(job_id, year, ticker)

    filing = filings[0]
    parsed_filing = filing.parse()

    if section_name not in parsed_filing.sections:
        return skip(job_id, year, ticker)

    raw_section = parsed_filing.get_sec_section(section_name)

    return {
        "job_id": job_id,
        "year": year,
        "ticker": ticker,
        "status": "success",
        "filing": raw_section
    }
