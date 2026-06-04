import logging
from typing import Any


def get_logger(name: str) -> logging.Logger:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    return logging.getLogger(name)


def log_processing_status(
    logger: logging.Logger,
    *,
    doc_id: str | None,
    source_file: str,
    status: str,
    warnings_count: int = 0,
    duration_seconds: float | None = None,
    debug: bool = False,
    error: Exception | None = None,
) -> None:
    payload: dict[str, Any] = {
        "doc_id": doc_id,
        "source_file": source_file,
        "status": status,
        "warnings_count": warnings_count,
    }
    if duration_seconds is not None:
        payload["duration_seconds"] = round(duration_seconds, 3)
    if debug and error is not None:
        payload["exception_type"] = type(error).__name__
        payload["error"] = str(error)[:300]
    logger.info("ragdocforge_status %s", payload)
