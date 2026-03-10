import uuid
from celery import group

from app.tasks.fetch_tasks import fetch_filing


def trigger_fetch(ticker: str, years: list[int]):

    job_id = str(uuid.uuid4())

    tasks = []

    for year in years:

        task = fetch_filing.s(
            ticker,
            year
        )

        tasks.append(task)

    job = group(tasks)

    result = job.apply_async()

    return {
        "job_id": job_id,
        "celery_group_id": result.id
    }
