"""Разбор файла субтитров на блоки 'Слайд N' с фразами.

Поддерживает два формата строк под маркером 'Слайд N':

1. С явными тайм-кодами:
       Слайд 1
       [00:00] Первое предложение.
       [00:03] Второе предложение.

2. Без тайм-кодов (каждая строка — отдельная фраза):
       Слайд 1
       Первое предложение.
       Второе предложение.

Фразы с явным тайм-кодом получают start_time из него.
Фразы без тайм-кода получают start_time=None — их временные
границы вычисляются равномерным делением в matcher.py по
длительности аудио слайда.

end_time последней фразы = None (заполняется в matcher.py).
"""
from __future__ import annotations

import re
from pathlib import Path

from src.models import SubtitlePhrase
from src.utils.logging_setup import get_logger
from src.utils.timecode import parse_timecode

logger = get_logger("subtitle_parser")

_BLOCK_RE = re.compile(r"^(?:слайд|slide)\s*(\d+)\s*$", re.IGNORECASE)
_PHRASE_RE = re.compile(r"^(\[[\d:.]+\])\s*(.*)$")


def parse_subtitles(path: str) -> dict[int, list[SubtitlePhrase]]:
    """Разбирает txt в словарь {номер слайда: [фразы]}."""
    blocks: dict[int, list[SubtitlePhrase]] = {}
    current_number: int | None = None
    current_texts: list[tuple[float | None, str]] = []

    lines = Path(path).read_text(encoding="utf-8").splitlines()
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        block_match = _BLOCK_RE.match(line)
        if block_match:
            _flush_block(blocks, current_number, current_texts)
            current_number = int(block_match.group(1))
            current_texts = []
            continue
        if current_number is None:
            continue
        phrase_match = _PHRASE_RE.match(line)
        if phrase_match:
            start = parse_timecode(phrase_match.group(1))
            text = phrase_match.group(2).strip()
            current_texts.append((start, text))
        else:
            current_texts.append((None, line))

    _flush_block(blocks, current_number, current_texts)
    logger.info("Разобрано блоков субтитров: %d", len(blocks))
    return blocks


def _flush_block(
    blocks: dict[int, list[SubtitlePhrase]],
    number: int | None,
    texts: list[tuple[float | None, str]],
) -> None:
    """Превращает накопленные (start|None, text) в фразы."""
    if number is None or not texts:
        return
    phrases = [
        SubtitlePhrase(text=text, start_time=start, end_time=None)
        for start, text in texts
        if text
    ]
    blocks[number] = phrases
