"""Centralized logging module."""
import logging
from typing import Optional


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get or create a logger with the specified name.
    
    Args:
        name: Logger name. If None, uses the caller's module name.
        
    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(name or __name__)
    
    # Only add handler if not already configured
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger
