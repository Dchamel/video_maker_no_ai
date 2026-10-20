"""Модели данных проекта.

Чистые dataclasses, без внешних зависимостей — основа для обмена
данными между модулями сканирования, сопоставления и рендеринга.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SubtitlePhrase:
    """Одна фраза субтитра с временным диапазоном показа (в секундах)."""
    text: str
    start_time: float
    end_time: float | None = None


@dataclass
class Slide:
    """Слайд: изображение + аудио + субтитры, связанные по номеру."""
    number: int
    image_path: str
    audio_path: str
    audio_duration: float = 0.0
    subtitles: list[SubtitlePhrase] = field(default_factory=list)

    @property
    def duration(self) -> float:
        """Длительность показа слайда = длительность его аудиодорожки."""
        return self.audio_duration


@dataclass
class Project:
    """Собранный проект: набор слайдов и путь к исходной папке."""
    name: str
    path: str
    slides: list[Slide] = field(default_factory=list)

    @property
    def total_duration(self) -> float:
        """Суммарная длительность всех слайдов."""
        return sum(s.duration for s in self.slides)
