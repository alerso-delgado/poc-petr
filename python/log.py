# python/log.py
import os
import sys
import logging

from typing import Optional

def initialize_log(log_name: str, log_file:  Optional[str] = None) -> logging.Logger:
    """
    Initialize and configure a logger with the specified log name.

    This function creates a logger and configures it to write log messages to the console and optionally to a file.
    The log messages will include the timestamp, log level, logger name, and the log message itself.

    Args:
        log_name (str): The name to be associated with the logger.
        log_file (str, optional): The path to the log file. Default is None.

    Returns:
        logging.Logger: The initialized logger object.

    Example:
        >>> app_log = initialize_log("APP_LOG")
        >>> app_log.debug("Debug message")
        [2023-06-30 10:00:00] — DEBUG    — APP_LOG  — Debug message
    """

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter("[%(asctime)s] — %(levelname)-8s — %(name)-8s — %(message)s"))

    # Create logger and add console handler
    log = logging.getLogger(log_name)
    log.setLevel(logging.DEBUG)
    log.addHandler(console_handler)
    
    # Add file handler if log_file is provided
    if log_file:
        if log_file is True:
            log_file = os.path.join(os.getcwd(), "app")  # Using current working directory and "app.log" as the default log file path
        file_handler = logging.FileHandler(f'{log_file}.log')
        file_handler.setFormatter(logging.Formatter("[%(asctime)s] — %(levelname)-8s — %(name)-8s — %(message)s"))
        log.addHandler(file_handler)

    log.propagate = False
    return log