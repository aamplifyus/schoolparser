import logging
import time
from functools import wraps

logger = logging.getLogger(__name__)


def timed(func):
    """Log the execution time for the decorated function."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger.info("{} with arguments ({}) ran in {}s".format(func.__name__, args, round(end - start, 2)))
        return result

    return wrapper
