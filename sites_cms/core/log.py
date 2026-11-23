import json
import logging
from datetime import UTC, datetime

EXTRA_FIELDS = ("method", "path", "status", "duration_ms")


class JsonFormatter(logging.Formatter):
    """Write each log record as one JSON object on one line."""

    def format(self, record):
        entry = {
            "time": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for field in EXTRA_FIELDS:
            if hasattr(record, field):
                entry[field] = getattr(record, field)
        # Django attaches these to its own error records.
        if "status" not in entry and hasattr(record, "status_code"):
            entry["status"] = record.status_code
        request = getattr(record, "request", None)
        if "path" not in entry and hasattr(request, "path"):
            entry["path"] = request.path
        if record.exc_info:
            entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(entry, default=str)
