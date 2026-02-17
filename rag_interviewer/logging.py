import logging


def get_logger(name: str | None = None) -> logging.Logger:
    """Return a configured logger for the given module name.

    Lightweight, centralized logger with a single StreamHandler if not already configured.
    """
    logger = logging.getLogger(name or __name__)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger
