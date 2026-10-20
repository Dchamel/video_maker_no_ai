"""Сканирование папки проекта: поиск jpg/wav/txt и извлечение номеров."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from src.utils.logging_setup import get_logger

logger = get_logger("scanner")

_NUMBER_RE = re.compile(r"(\d+)")
_IMAGE_EXTS = {".jpg", ".jpeg", ".png"}
_AUDIO_EXTS = {".wav"}


@dataclass
class ScannedFiles:
    """Результат сканирования: номер -> путь для изображений и аудио."""
    images: dict[int, str]
    audios: dict[int, str]
    txt_path: str | None


def _extract_number(stem: str) -> int | None:
    """Извлекает первое целое число из имени файла (без расширения)."""
    match = _NUMBER_RE.search(stem)
    return int(match.group(1)) if match else None


def scan_project(project_path: str) -> ScannedFiles:
    """Сканирует папку проекта и собирает найденные файлы по номерам."""
    folder = Path(project_path)
    if not folder.is_dir():
        raise FileNotFoundError(f"Папка проекта не найдена: {project_path}")

    images: dict[int, str] = {}
    audios: dict[int, str] = {}
    txt_path: str | None = None

    for entry in sorted(folder.iterdir()):
        if not entry.is_file():
            continue
        suffix = entry.suffix.lower()
        if suffix in _IMAGE_EXTS:
            num = _extract_number(entry.stem)
            if num is not None:
                images[num] = str(entry)
        elif suffix in _AUDIO_EXTS:
            num = _extract_number(entry.stem)
            if num is not None:
                audios[num] = str(entry)
        elif suffix == ".txt":
            txt_path = str(entry)

    logger.info(
        "Найдено: %d изображений, %d аудио, txt=%s",
        len(images), len(audios), txt_path is not None,
    )
    return ScannedFiles(images=images, audios=audios, txt_path=txt_path)
