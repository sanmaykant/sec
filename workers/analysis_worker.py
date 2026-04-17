from app.core.celery_app import celery_app

if __name__ == "__main__":
    celery_app.conf.update(
        task_prefetch_multiplier=1,      # Only take 1 task at a time
        task_acks_late=True              # Don't acknowledge until finished
    )

    celery_app.worker_main([
        "worker",
        "--loglevel=info",
        "-Q", "analysis_queue",
        "--pool=solo",                   # Use 'solo' pool for maximum isolation
        "-c", "1"
    ])
