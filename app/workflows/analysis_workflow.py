import uuid
import time
import logging
import os

from celery import chain, group, chord

from app.tasks.fetch_tasks import fetch_filing
from app.tasks.embedding_tasks import embed_text
from app.services.edgar_service import EdgarService


my_logger = logging.getLogger("my_app_logger")
my_logger.setLevel(logging.INFO)

import json

def prettify_output(outputs, max_sentence_length=100, max_embedding_length=10):
    pretty_output = []
    
    for obj in outputs:
        if obj.get("status") != "success":
            continue
        
        chunks = obj.get("chunks", [])
        embeddings = obj.get("embeddings", [])
        
        truncated_chunks = []
        truncated_embeddings = []
        
        for chunk, emb in zip(chunks, embeddings):
            if len(chunk) > max_sentence_length:
                chunk = chunk[:max_sentence_length] + "..."
            truncated_chunks.append(chunk)
            
            if len(emb) > max_embedding_length:
                emb = emb[:max_embedding_length] + ["..."]
            truncated_embeddings.append(emb)
        
        pretty_obj = {
            "chunks": truncated_chunks,
            "embeddings": truncated_embeddings,
            "year": obj.get("year", "Unknown")
        }
        
        pretty_output.append(pretty_obj)
    
    # print(json.dumps(pretty_output, indent=2))
    print(len(pretty_output))
    for out in pretty_output:
        print(out["year"])
    for out in outputs:
        if "filing" not in out or out.get("filing", "").strip() == "":
            continue
        dir_path = f"outputs/{out['ticker']}"
        os.makedirs(dir_path, exist_ok=True)
        with open(f"outputs/{out["ticker"]}/{out["year"]}", "w") as file:
            file.write(out["filing"])

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
                embed_text.s()
                )

        pipelines.append(pipeline)

    my_logger.debug(f"Total number of tasks for ticker {ticker} : {len(pipelines)}")
    job = group(pipelines)

    start_time = time.time()

    result = job.apply_async()
    outputs = result.get()

    duration = time.time() - start_time
    my_logger.info(f"All pipelines completed in {duration:.2f} seconds")

    # my_logger.info(f"Embeddings: {outputs}")
    prettify_output(outputs)

    return job_id
