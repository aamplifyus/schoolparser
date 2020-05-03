import logging
import time
from functools import wraps
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

from eztrack.base.config.config import EZTrack_metric_log_name


def _setup_log(log_fname, log_handler_type):
    logger = logging.getLogger(__name__)

    logger.setLevel(logging.DEBUG)
    if log_handler_type == "rotate":
        file_handler = RotatingFileHandler(log_fname, maxBytes=20000, backupCount=10)
    else:
        file_handler = TimedRotatingFileHandler(log_fname, when="D")
        # file_handler.mode = 'w'
    formatter = logging.Formatter(
        "%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d]: %(message)s"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.propagate = False
    return logger


def timed(func):
    """Log the execution time for the decorated function."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger = _setup_log(EZTrack_metric_log_name, "rotate")
        logger.info("{} ran in {}s".format(func.__name__, round(end - start, 2)))
        return result

    return wrapper


def counted(event):
    """Log the number of occurrences of an event."""
    logger = _setup_log(EZTrack_metric_log_name, "rotate")
    logger.info(f"{event} occurred.")
