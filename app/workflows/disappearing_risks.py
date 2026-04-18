import uuid
import time
from celery import chain, chord

from app.tasks.fetch_tasks import fetch_filing
from app.tasks.embedding_tasks import embed_text
from app.tasks.topic_tasks import topic_modelling, topic_modellingg

import logging

my_logger = logging.getLogger("my_app_logger")
my_logger.setLevel(logging.INFO)


def dr_analysis(ticker: str, year: int):
    job_id = str(uuid.uuid4())
    my_logger.info(f"Analysis begun for ticker {ticker}")

    header = []
    for y in range(2020, year+1):
        header.append(
            chain(
                fetch_filing.s(job_id, ticker, y, "10-K", "part_i_item_1a"), 
                embed_text.s()
            )
        )

    callback = topic_modelling.s(year)

    start_time = time.time()

    result = chord(header)(callback)
    
    final_output = result.get()

    duration = time.time() - start_time
    my_logger.info(f"Full pipeline (Embed -> Topic) completed in {duration:.2f} seconds")
    
    return final_output

def dr_analysiss(ticker: str, year: int):
    job_id = str(uuid.uuid4())
    my_logger.info(f"Analysis begun for ticker {ticker}")

    header = []
    for y in range(2021, year+1):
        header.append(
            chain(
                fetch_filing.s(job_id, ticker, y, "10-K", "part_i_item_1a"), 
                embed_text.s()
            )
        )

    callback = topic_modellingg.s(year)

    start_time = time.time()

    result = chord(header)(callback)
    
    final_output = result.get()

    duration = time.time() - start_time
    my_logger.info(f"Full pipeline (Embed -> Topic) completed in {duration:.2f} seconds")
    
    return final_output
