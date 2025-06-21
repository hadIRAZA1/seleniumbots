import logging
import uuid
from pythonjsonlogger import jsonlogger
from datetime import datetime
import os # Import os module

# Define LOG_FILE relative to your project's root, inside a 'logs' directory
LOG_FILE = os.path.join("logs", "automation_logs.jsonl")

def get_logger(script_name):
    """
    Sets up a logger to write structured JSON to a file.
    """
    logger = logging.getLogger(script_name)
    logger.setLevel(logging.INFO)
    
    # Prevent logs from being propagated to the root logger
    logger.propagate = False

    # Ensure the log directory exists
    log_dir = os.path.dirname(LOG_FILE)
    if log_dir and not os.path.exists(log_dir): # Check if log_dir is not empty string
        os.makedirs(log_dir, exist_ok=True)

    # Use a file handler to write to our log file
    log_handler = logging.FileHandler(LOG_FILE)

    # Create a unique ID for each run of the script
    run_id = str(uuid.uuid4())

    # Use a custom JSON formatter
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    log_handler.setFormatter(formatter)

    # Add the handler to the logger if it doesn't have one already
    if not logger.handlers:
        logger.addHandler(log_handler)
    
    # Return a logger instance that includes the run_id in each message
    return logging.LoggerAdapter(logger, {'run_id': run_id})