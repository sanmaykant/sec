import os
import logging


class Settings:

    REDIS_URL = os.getenv(
        "REDIS_URL",
        "redis://localhost:6379/0"
    )

    logger = logging.getLogger("my_app_logger")

settings = Settings()
settings.logger.setLevel(logging.INFO)
logger = settings.logger
