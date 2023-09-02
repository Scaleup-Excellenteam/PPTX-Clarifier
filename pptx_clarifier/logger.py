import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler

root = sys.path[1]


def setup_log(name, log_file):
    logs_directory = os.path.join(root, "pptx_clarifier", "logs", name)
    os.makedirs(logs_directory, exist_ok=True)
    log_file = os.path.join(logs_directory, f"{log_file}.log")
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Define logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create a TimedRotatingFileHandler and add it to the logger
    file_handler = TimedRotatingFileHandler(log_file, when='midnight', interval=1, backupCount=5)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    console_handler.setFormatter(formatter)

    # Add the console handler to the logger
    logger.addHandler(console_handler)

    return logger
