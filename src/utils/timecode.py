"""Парсинг и форматирование тайм-кодов вида [mm:ss]."""
from __future__ import annotations

import re

# Поддерживаем [mm:ss], [mm:ss.s], [mm:ss.sss], а также [hh:mm:ss]
_PATTERN = re.compile(r"\[(?:(\d+):)?(\d+):(\d+(?:\.\d+)?)\]")


def parse_timecode(value: str) -> float:
    """Преобразует '[mm:ss]' (или с часами/долями секунды) в секунды.

    Если передано чистое число — воспринимает как секунды.
    """
    value = value.strip()
    match = _PATTERN.fullmatch(value)
    if match:
        hours = int(match.group(1)) if match.group(1) else 0
        minutes = int(match.group(2))
        seconds = float(match.group(3))
        return hours * 3600 + minutes * 60 + seconds
    return float(value)


def format_timecode(seconds: float) -> str:
    """Форматирует секунды в '[mm:ss.ss]'."""
    seconds = max(0.0, float(seconds))
    minutes = int(seconds // 60)
    secs = seconds - minutes * 60
    return f"[{minutes:02d}:{secs:05.2f}]"
