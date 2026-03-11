from app.core.celery_app import celery_app

celery_app.autodiscover_tasks(["app.tasks.embedding_tasks"])

if __name__ == "__main__":

    celery_app.worker_main([
        "worker",
        "--loglevel=info",
        "-Q",
        "embed_queue",
        "-c",
        "4"
    ])
