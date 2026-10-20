"""Централизованная конфигурация всех параметров сборки видео.

Параметры для main.py задаются здесь (или переопределяются через CLI).
В notebook.ipynb те же параметры задаются в первой ячейке.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict


@dataclass
class VideoConfig:
    """Параметры выходного видеопотока."""
    width: int = 1920
    height: int = 1080
    fps: int = 30
    codec: str = "libx264"
    output_format: str = "mp4"


@dataclass
class SubtitleConfig:
    """Параметры отрисовки субтитров поверх слайда."""
    font_path: str = "arial.ttf"
    font_size: int = 48
    font_color: tuple[int, int, int] = (255, 255, 255)
    # Положение: 'bottom', 'top', 'center'
    position: str = "bottom"
    margin: int = 60
    # Полупрозрачная подложка под текстом для читаемости
    background_color: tuple[int, int, int, int] = (0, 0, 0, 160)
    background_padding: int = 12


@dataclass
class TransitionConfig:
    """Параметры анимации перехода между слайдами."""
    # Доступные: 'none', 'fade', 'crossfade', 'slide_left'
    type: str = "crossfade"
    duration: float = 0.5


@dataclass
class Config:
    """Корневая конфигурация пайплайна."""
    project_path: str = "input/Ролик 1"
    output_path: str = "output/Ролик 1.mp4"
    video: VideoConfig = field(default_factory=VideoConfig)
    subtitle: SubtitleConfig = field(default_factory=SubtitleConfig)
    transition: TransitionConfig = field(default_factory=TransitionConfig)

    @classmethod
    def default(cls) -> "Config":
        """Конфигурация по умолчанию."""
        return cls()

    def to_dict(self) -> dict:
        """Сериализация в словарь (для логирования/ноутбука)."""
        return asdict(self)
