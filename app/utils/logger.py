import logging
import os
from logging.handlers import RotatingFileHandler

from app.config import LOG_DIR

# Ensure the logs directory exists
os.makedirs(LOG_DIR, exist_ok=True)


def get_logger(name: str = "QuantScoreAPI") -> logging.Logger:
    """
    Create or retrieve a configured application logger.

    Uses rotating file logs for persistence and console
    output for local development visibility.
    """
    logger = logging.getLogger(name)

    # Avoid adding multiple handlers if logger already exists
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    # --------------------------
    # File handler (rotating)
    # --------------------------
    file_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, "quantscore.log"),
        maxBytes=2_000_000,
        backupCount=5,
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # --------------------------
    # Console handler (dev)
    # --------------------------
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
