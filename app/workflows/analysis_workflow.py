import uuid
import time
import logging

from celery import chain, group, chord

from app.tasks.fetch_tasks import fetch_filing
from app.tasks.extraction_tasks import extract_section
from app.services.edgar_service import EdgarService


my_logger = logging.getLogger("my_app_logger")
my_logger.setLevel(logging.INFO)

def start_analysis(ticker: str):

    my_logger.info(f"Analysis begun for ticker {ticker}")

    job_id = str(uuid.uuid4())

    service = EdgarService()
    date_range = service.fetch_date_range(ticker=ticker, form="10-K")
    my_logger.debug(f"Date range for ticker {ticker} : {date_range}")

    pipelines = []

    for year in range(date_range[0].year, date_range[1].year + 1):
        my_logger.debug(f"Dispatching task for ticker {ticker} and year {year}")

        pipeline = chain(
                fetch_filing.s(job_id, ticker, year, "10-K", "part_i_item_1a"),
                extract_section.s()
                )

        pipelines.append(pipeline)

    my_logger.debug(f"Total number of tasks for ticker {ticker} : {len(pipelines)}")
    job = group(pipelines)

    start_time = time.time()

    result = job.apply_async()
    outputs = result.get()

    duration = time.time() - start_time
    my_logger.info(f"All pipelines completed in {duration:.2f} seconds")

    return job_id
