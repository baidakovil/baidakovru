import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging():
    # Create logs directory if it doesn't exist
    log_dir = "/var/log/baidakovru"
    os.makedirs(log_dir, exist_ok=True)

    # Set up formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)-30s - %(levelname)-5s - %(filename)-25s:%(lineno)-5d - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s - %(message)s'
    )

    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Set to DEBUG to capture all levels

    # Only add handlers if they don't already exist
    if not root_logger.handlers:
        # Create a rotating file handler for DEBUG and above
        file_handler = RotatingFileHandler(
            f"{log_dir}/app.log", maxBytes=10240, backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)

        # Create a console handler for INFO and above
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)

        # Add handlers to root logger
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

    # Set APScheduler logger level
    logging.getLogger('apscheduler').setLevel(logging.INFO)

    # Create a custom logger that inherits from root logger
    logger = logging.getLogger('baidakov_app')

    return logger
