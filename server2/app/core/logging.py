import logging
import sys


def build_logger(name: str, level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level.upper())
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
        logger.addHandler(handler)
    logger.propagate = False
    return logger
