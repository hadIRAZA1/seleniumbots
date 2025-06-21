import logging
import json
import os
import time

class JsonFormatter(logging.Formatter):
    """
    A custom formatter to output log records as JSON lines.
    """
    def format(self, record):
        log_entry = {
            "timestamp": time.time(), # Unix timestamp
            "level": record.levelname,
            "script_name": getattr(record, 'script_name', 'UNKNOWN'), # Custom attribute for script name
            "message": record.getMessage(),
        }

        # Add extra attributes if they exist
        if hasattr(record, 'status'):
            log_entry['status'] = record.status
        if hasattr(record, 'screenshot'):
            log_entry['screenshot'] = record.screenshot
        if record.exc_info:
            # Format exception traceback if present
            log_entry['traceback'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry)

def get_logger(script_name="default", log_file_name="automation_logs_jsonl"):
    """
    Configures and returns a logger instance for a specific script.
    It ensures only one FileHandler is added to the root logger for the JSONL file.
    """
    logger = logging.getLogger() # Get the root logger
    logger.setLevel(logging.INFO) # Set global logging level to INFO or DEBUG to capture all messages

    # Prevent duplicate handlers if get_logger is called multiple times
    if not any(isinstance(handler, logging.FileHandler) and handler.baseFilename.endswith(log_file_name) for handler in logger.handlers):
        # --- CHANGE IS HERE ---
        # Set log_dir to an empty string to put the file in the current working directory
        log_dir = "" 
        # ----------------------
        
        # Note: No need to os.makedirs(log_dir) if it's an empty string,
        # as it refers to the current directory which already exists.
        # However, for consistency with previous versions, you can keep the check.
        if log_dir and not os.path.exists(log_dir): # Added 'if log_dir' check
            os.makedirs(log_dir)
        
        log_path = os.path.join(log_dir, log_file_name)

        file_handler = logging.FileHandler(log_path, mode='a', encoding='utf-8')
        file_handler.setFormatter(JsonFormatter())
        logger.addHandler(file_handler)

        # Optional: Add a StreamHandler to see logs in console during development
        if not any(isinstance(handler, logging.StreamHandler) for handler in logger.handlers):
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            logger.addHandler(stream_handler)

    script_logger = logging.getLogger(script_name)
    script_logger.setLevel(logging.INFO) 
    
    return script_logger

# Example usage (for testing file_logger.py directly)
if __name__ == "__main__":
    test_logger1 = get_logger(script_name="TestScript1")
    test_logger1.info("This is an info message from TestScript1.")
    test_logger1.warning("This is a warning from TestScript1.", extra={'status': 'PENDING'})
    try:
        raise ValueError("Something went wrong in TestScript1!")
    except ValueError:
        test_logger1.error("An error occurred!", exc_info=True, extra={'screenshot': 'error_screenshot.png'})

    test_logger2 = get_logger(script_name="TestScript2")
    test_logger2.debug("This debug message might not show if root level is INFO.")
    test_logger2.info("Another info message from TestScript2.")

    print(f"Log file '{os.path.join('', 'automation_logs_jsonl')}' should be updated.")