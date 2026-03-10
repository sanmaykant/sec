import uuid
import logging
from celery import chain, group, chord

from app.tasks.fetch_tasks import fetch_filing
# from app.tasks.parse_tasks import parse_risk_section
# from app.tasks.embed_tasks import embed_chunks
# from app.tasks.similarity_tasks import compute_similarity

from app.services.edgar_service import EdgarService


my_logger = logging.getLogger("my_app_logger")
my_logger.setLevel(logging.WARNING)

def start_analysis(ticker: str):

    job_id = str(uuid.uuid4())

    service = EdgarService()
    date_range = service.fetch_date_range(ticker=ticker, form="10-K")
    my_logger.debug(f"Date range for ticker {ticker} : {date_range}")

    tasks = []

    for year in range(date_range[0].year, date_range[1].year + 1):
        my_logger.debug(f"Dispatching task for ticker {ticker} and year {year}")

        task = fetch_filing.s(job_id, ticker, year, "10-K")

        tasks.append(task)

    my_logger.debug(f"Total number of tasks for ticker {ticker} : {len(tasks)}")
    job = group(tasks)

    result = job.apply_async()

    return job_id
