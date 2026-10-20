"""Централизованная конфигурация всех параметров сборки видео.

Параметры для main.py задаются здесь (или переопределяются через CLI).
В notebook.ipynb те же параметры задаются в первой ячейке.

Каждый параметр снабжён комментарием на русском — что он делает
и какое значение по умолчанию.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict


# --- Пресеты качества видео -------------------------------------------------
# Ключ — высота кадра в пикселях. Ширина считается для соотношения 16:9.
# Выбор пресета через Config.quality (строка) или флаг CLI --quality.
QUALITY_PRESETS: dict[str, tuple[int, int]] = {
    "360p": (640, 360),
    "480p": (854, 480),
    "720p": (1280, 720),
    "1080p": (1920, 1080),
    "2k": (2560, 1440),
    "4k": (3840, 2160),
}
DEFAULT_QUALITY = "720p"  # разумный баланс качества и размера/скорости


@dataclass
class VideoConfig:
    """Параметры выходного видеопотока."""
    # Пресет качества: '360p', '480p', '720p', '1080p', '2k', '4k'.
    # Задаёт ширину/высоту из QUALITY_PRESETS. По умолчанию 720p.
    quality: str = DEFAULT_QUALITY
    # Частота кадров в секунду. 30 — плавно, 24 — кинематографично.
    fps: int = 30
    # Видеокодек. libx264 — универсальный, хорошо сжимает.
    codec: str = "libx264"
    # Формат контейнера на выходе.
    output_format: str = "mp4"

    @property
    def resolution(self) -> tuple[int, int]:
        """(ширина, высота) из пресета качества."""
        return QUALITY_PRESETS.get(self.quality, QUALITY_PRESETS[DEFAULT_QUALITY])

    @property
    def width(self) -> int:
        return self.resolution[0]

    @property
    def height(self) -> int:
        return self.resolution[1]


@dataclass
class SubtitleConfig:
    """Параметры отрисовки субтитров поверх слайда.

    Отступы задаются В ПРОЦЕНТАХ от размеров кадра — так они
    автоматически масштабируются при смене качества (360p..4k).
    """
    # Путь к файлу шрифта (.ttf/.otf). Если не найден — встроенный.
    font_path: str = "arial.ttf"
    # Базовый размер шрифта для 1080p. Автомасштабируется под реальное
    # разрешение (меньше для 720p, больше для 4k).
    font_size: int = 48
    # Цвет текста (R, G, B). Белый по умолчанию.
    font_color: tuple[int, int, int] = (255, 255, 255)
    # Позиция блока субтитров: 'bottom', 'top', 'center'.
    position: str = "bottom"
    # Отступ от левого края, % от ширины кадра. Защищает от вылета текста.
    margin_left_pct: float = 5.0
    # Отступ от правого края, % от ширины кадра.
    margin_right_pct: float = 5.0
    # Отступ снизу, % от высоты кадра (используется при position='bottom').
    margin_bottom_pct: float = 8.0
    # Отступ сверху, % от высоты кадра (используется при position='top').
    margin_top_pct: float = 8.0
    # Макс. число строк при переносе длинной фразы (word-wrap).
    # Если фраза длиннее доступной ширины — разбивается на строки.
    max_lines: int = 3
    # Полупрозрачная подложка под текстом (R, G, B, A) для читаемости.
    background_color: tuple[int, int, int, int] = (0, 0, 0, 160)
    # Отступ подложки вокруг текста в пикселях.
    background_padding: int = 12


@dataclass
class AudioConfig:
    """Параметры обработки звука.

    По умолчанию нормализация ВЫКЛючена — звук остаётся как в исходных
    WAV-файлах. Включите normalize=True, чтобы привести громкость всех
    сегментов к единому уровню.
    """
    # Включить выравнивание громкости. False — звук как в файлах.
    normalize: bool = False
    # Целевой уровень громкости в процентах от автоопределённого.
    # 100 = без изменений (только выравнивание), 120 = +20%, 80 = -20%.
    # Применяется поверх единого уровня, если normalize=True.
    gain_percent: float = 100.0


@dataclass
class TransitionConfig:
    """Параметры анимации перехода между слайдами."""
    # Доступные: 'none', 'fade', 'crossfade', 'slide_left'
    type: str = "crossfade"
    # Длительность перехода в секундах.
    duration: float = 0.5


@dataclass
class Config:
    """Корневая конфигурация пайплайна."""
    project_path: str = "input/Ролик"
    output_path: str = "output/Ролик.mp4"
    video: VideoConfig = field(default_factory=VideoConfig)
    subtitle: SubtitleConfig = field(default_factory=SubtitleConfig)
    audio: AudioConfig = field(default_factory=AudioConfig)
    transition: TransitionConfig = field(default_factory=TransitionConfig)

    @classmethod
    def default(cls) -> "Config":
        """Конфигурация по умолчанию."""
        return cls()

    def to_dict(self) -> dict:
        """Сериализация в словарь (для логирования/ноутбука)."""
        return asdict(self)
