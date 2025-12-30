import logging
from logging.handlers import RotatingFileHandler
import os
from app.config import LOG_DIR

# Ensure the logs directory exists
os.makedirs(LOG_DIR, exist_ok=True)

def get_logger(name="QuantScoreAPI"):
    logger = logging.getLogger(name)

    # Avoid adding multiple handlers if logger already exists
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # File handler
    file_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, "quantscore.log"),
        maxBytes=2_000_000,
        backupCount=5
    )
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console output for development
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
