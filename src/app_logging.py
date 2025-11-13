"""Define logging configuration for the application."""

import logging
import sys
import time

# pylint: disable=R0903


class OnlyWarningFilter(logging.Filter):
    """Filter to allow only WARNING level logs"""

    def filter(self, record):
        return record.levelno == logging.WARNING


class OnlyInfoFilter(logging.Filter):
    """Filter to allow only INFO level logs"""

    def filter(self, record):
        return record.levelno == logging.INFO


class OnlyErrorFilter(logging.Filter):
    """Filter to allow only ERROR level logs"""

    def filter(self, record):
        return record.levelno == logging.ERROR


# Configure root logger to output to stdout (console)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

# Custom log formatter
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
formatter.converter = time.gmtime  # Use UTC time

# Create handlers for different levels
info_handler = logging.StreamHandler(sys.stdout)
info_handler.setLevel(logging.INFO)
info_handler.addFilter(OnlyInfoFilter())
info_handler.setFormatter(formatter)

error_handler = logging.StreamHandler(sys.stdout)
error_handler.setLevel(logging.ERROR)
error_handler.addFilter(OnlyErrorFilter())
error_handler.setFormatter(formatter)

debug_handler = logging.StreamHandler(sys.stdout)
debug_handler.setLevel(logging.DEBUG)
debug_handler.setFormatter(formatter)

warning_handler = logging.StreamHandler(sys.stdout)
warning_handler.setLevel(logging.WARNING)
warning_handler.addFilter(OnlyWarningFilter())
warning_handler.setFormatter(formatter)

# Get the main logger and attach handlers
logger = logging.getLogger("my_logger")
logger.setLevel(logging.DEBUG)  # Capture all levels
logger.addHandler(info_handler)
logger.addHandler(error_handler)
logger.addHandler(debug_handler)
logger.addHandler(warning_handler)

logger.propagate = False
# Optional: example usage
# logger.info("This is an info message")
# logger.error("This is an error message")
