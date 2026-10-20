"""Единый логгер для всего проекта."""
from __future__ import annotations

import logging
import sys

_CONFIGURED = False


def get_logger(name: str = "video_maker") -> logging.Logger:
    """Возвращает настроенный логгер с выводом в stdout."""
    global _CONFIGURED
    logger = logging.getLogger(name)
    if not _CONFIGURED:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)s | %(message)s",
                datefmt="%H:%M:%S",
            )
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
        _CONFIGURED = True
    return logger
