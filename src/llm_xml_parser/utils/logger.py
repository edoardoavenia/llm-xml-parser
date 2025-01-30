import logging
import sys

def get_logger(name: str) -> logging.Logger:
    """
    Returns a logger with a predefined configuration.
    Logs to stdout at DEBUG level for simplicity.
    """
    # Create logger instance
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Check if logger has handlers already (to avoid duplicate logs)
    if not logger.handlers:
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)

        # Create a formatter
        formatter = logging.Formatter(
            fmt="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(formatter)

        # Add console handler to logger
        logger.addHandler(console_handler)

    return logger
