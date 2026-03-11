from app.core.celery_app import celery_app


@celery_app.task(
    queue="extract_queue",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3}
)
def extract_section(fetch_result, section="part_i_item_1a"):
    if fetch_result.get("status") != "success":
        return fetch_result

    return {
        "extracted": fetch_result["filing"]
    }
