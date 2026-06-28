"""Structured logging setup using structlog.

Renders JSON logs in production and pretty colored logs in development.
Privacy note: never log patient PII here -- log identifiers (patient_id) only.
"""

import logging
import sys

import structlog

from app.config import settings


def configure_logging() -> None:
    """Configure structlog + stdlib logging for the whole app."""

    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # Route stdlib logging (uvicorn, sqlalchemy, etc.) through stdout.
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    shared_processors: list = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if settings.is_production:
        renderer: structlog.types.Processor = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=[*shared_processors, renderer],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Return a bound structlog logger."""
    return structlog.get_logger(name)
