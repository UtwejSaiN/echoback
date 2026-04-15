import logging
import sys

def setup_logging(level=logging.INFO):
    """Configure logging for application"""

    # Create logger
    logger = logging.getLogger('c3tm')
    logger.setLevel(level)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(formatter)

    # Add handler
    logger.addHandler(console_handler)

    return logger
