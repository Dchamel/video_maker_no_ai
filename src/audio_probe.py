"""Вычисление длительности WAV через стандартный модуль wave.

Без внешних зависимостей — используется только встроенный модуль wave.
"""
from __future__ import annotations

import wave
from pathlib import Path

from src.utils.logging_setup import get_logger

logger = get_logger("audio_probe")


def get_wav_duration(path: str) -> float:
    """Возвращает длительность WAV-файла в секундах."""
    with wave.open(str(path), "rb") as wav:
        nframes = wav.getnframes()
        framerate = wav.getframerate()
    if framerate == 0:
        raise ValueError(f"Нулевая частота кадров в WAV: {path}")
    duration = nframes / framerate
    logger.debug("Длительность %s = %.2f с", Path(path).name, duration)
    return duration
