import logging
import json
import os
import time

# === JSON LOG FORMATTER ===
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": time.time(),
            "level": record.levelname,
            "script_name": getattr(record, 'script_name', 'UNKNOWN'),
            "message": record.getMessage(),
        }
        if hasattr(record, 'status'):
            log_entry['status'] = record.status
        if hasattr(record, 'screenshot'):
            log_entry['screenshot'] = record.screenshot
        if record.exc_info:
            log_entry['traceback'] = self.formatException(record.exc_info)
        return json.dumps(log_entry, ensure_ascii=False, indent=2)


# === FILTER TO REMOVE NOISY MODULES (webdriver_manager, urllib3) ===
class NoisyLoggerFilter(logging.Filter):
    def __init__(self):
        super().__init__()
        self.exclude_loggers = ['webdriver_manager', 'urllib3']

    def filter(self, record):
        return not any(record.name.startswith(name) for name in self.exclude_loggers)


def suppress_noisy_loggers():
    """Disable noisy external loggers completely."""
    for logger_name in ['webdriver_manager', 'urllib3']:
        noisy_logger = logging.getLogger(logger_name)
        noisy_logger.setLevel(logging.CRITICAL + 1)
        noisy_logger.propagate = False


# === LOGGER SETUP FUNCTION ===
def get_logger(script_name="default", log_file_name="automation_logs_jsonl"):
    suppress_noisy_loggers()

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    log_dir = ""  # Customize if needed
    log_path = os.path.join(log_dir, log_file_name)

    # File Handler: Write structured JSON logs
    if not any(isinstance(h, logging.FileHandler) and h.baseFilename.endswith(log_file_name) for h in logger.handlers):
        file_handler = logging.FileHandler(log_path, mode='a', encoding='utf-8')
        file_handler.setFormatter(JsonFormatter())
        file_handler.addFilter(NoisyLoggerFilter())
        logger.addHandler(file_handler)

    # Console Handler: Colorful readable logs
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter(
            "\033[1;34m%(asctime)s\033[0m - \033[1;32m%(name)s\033[0m - \033[1;33m%(levelname)s\033[0m - %(message)s"
        ))
        stream_handler.addFilter(NoisyLoggerFilter())
        logger.addHandler(stream_handler)

    # Return script-specific logger
    script_logger = logging.getLogger(script_name)
    script_logger.setLevel(logging.INFO)
    return script_logger


# === TEST CASE ===
if __name__ == "__main__":
    log = get_logger("TestScript")

    log.info("🔵 This is an info message.")
    log.warning("🟡 This is a warning.", extra={'status': 'PENDING'})

    try:
        raise ValueError("🚨 Simulated error!")
    except Exception:
        log.error("🔴 An error occurred!", exc_info=True, extra={'screenshot': 'error_screenshot.png'})

    # Verify noisy loggers are suppressed
    logging.getLogger('webdriver_manager.driver').info("This should NOT appear.")
    logging.getLogger('urllib3.connectionpool').info("This should also NOT appear.")

    print(f"✅ Log file saved as: {os.path.join(log_dir, log_file_name)}")
