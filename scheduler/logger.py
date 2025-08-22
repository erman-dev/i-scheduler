import logging
import sys


def get_logger(name: str):
    """Get a logger instance."""

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s | %(name)25s | %(levelname)6s | %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
