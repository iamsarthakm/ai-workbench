# log.py
import json
import logging
import os
from datetime import datetime, timezone

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_RECORD_ATTRIBUTES = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
}


class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "service": "__PROJECT_SLUG__",
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        # Collect extra fields not in log_entry and add them under "data"
        log_entry.update(
            {
                field: value
                for field, value in record.__dict__.items()
                if field not in LOG_RECORD_ATTRIBUTES and not field.startswith("_")
            }
        )
        # Add extra debugging information if in debug mode
        if record.levelno == logging.DEBUG:
            log_entry.update(
                {
                    "file": record.pathname,
                    "function": record.funcName,
                    "line": record.lineno,
                }
            )
        return json.dumps(log_entry)


def setup_logger(name="app"):
    root_logger = logging.getLogger(name)
    root_logger.setLevel(LOG_LEVEL)
    if not root_logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        root_logger.addHandler(handler)
    return root_logger
