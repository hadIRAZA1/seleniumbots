# file_logger.py (Your provided file with a small enhancement for log directory)
import logging
import uuid
from pythonjsonlogger import jsonlogger
from datetime import datetime
import os # Import os for path operations

# Define the log directory and file path
LOG_DIR = "logs"
LOG_FILE_PATH = os.path.join(LOG_DIR, "automation_logs.jsonl")

class JsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(JsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get('timestamp'):
            log_record['timestamp'] = datetime.fromtimestamp(record.created).isoformat()
        # Add custom fields from the LoggerAdapter's extra dict
        if hasattr(record, 'script_name'):
            log_record['script_name'] = record.script_name
        if hasattr(record, 'status'):
            log_record['status'] = record.status
        if hasattr(record, 'screenshot'):
            log_record['screenshot'] = record.screenshot
        if hasattr(record, 'run_id'): # From LoggerAdapter
            log_record['run_id'] = record.run_id
        # Ensure exc_info is included if present
        if record.exc_info:
            import traceback
            log_record['exc_info'] = self.formatException(record.exc_info)

def get_logger(script_name):
    """
    Sets up a logger to write structured JSON to a local file.
    """
    logger = logging.getLogger(script_name)
    logger.setLevel(logging.INFO)
    logger.propagate = False # Prevent logs from being propagated to the root logger

    # Create the log directory if it doesn't exist
    os.makedirs(LOG_DIR, exist_ok=True)

    # Use a file handler to write to our log file
    # Ensure only one file handler is added to avoid duplicate logs in the same process
    # This checks if a handler for this specific log file path already exists
    if not any(isinstance(h, logging.FileHandler) and h.baseFilename == os.path.abspath(LOG_FILE_PATH) for h in logger.handlers):
        file_handler = logging.FileHandler(LOG_FILE_PATH)
        formatter = JsonFormatter('%(asctime)s %(name)s %(levelname)s %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Add a filter to inject 'script_name' into the log record automatically
    class ScriptNameFilter(logging.Filter):
        def filter(self, record):
            record.script_name = script_name
            return True
    
    if not any(isinstance(f, ScriptNameFilter) for f in logger.filters):
        logger.addFilter(ScriptNameFilter(script_name))

    # Create a unique ID for each run of the script
    run_id = str(uuid.uuid4())
    # Return a logger adapter to inject `run_id` into each message's extra dict
    return logging.LoggerAdapter(logger, {'run_id': run_id})