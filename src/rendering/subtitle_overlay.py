"""Отрисовка субтитра в одну строку поверх кадра через Pillow.

Чистые функции: выбор активной фразы по времени и наложение текста
на numpy-кадр с настраиваемым шрифтом, размером, цветом и позицией.
"""
from __future__ import annotations

from typing import Sequence

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from config.default_config import SubtitleConfig
from src.models import SubtitlePhrase


def select_phrase(subtitles: Sequence[SubtitlePhrase], t: float) -> str | None:
    """Возвращает текст фразы, активной в момент времени t (секунды)."""
    for phrase in subtitles:
        end = phrase.end_time if phrase.end_time is not None else float("inf")
        if phrase.start_time <= t < end:
            return phrase.text
    return None


def draw_subtitle(
    frame: np.ndarray, text: str | None, config: SubtitleConfig
) -> np.ndarray:
    """Накладывает текст субтитра на кадр (numpy RGB) и возвращает новый кадр."""
    if not text:
        return frame
    img = Image.fromarray(frame).convert("RGBA")
    draw = ImageDraw.Draw(img, "RGBA")
    font = _load_font(config)

    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x, y = _compute_position(img.size, text_w, text_h, config)

    pad = config.background_padding
    draw.rectangle(
        (x - pad, y - pad, x + text_w + pad, y + text_h + pad),
        fill=config.background_color,
    )
    draw.text((x - bbox[0], y - bbox[1]), text, font=font, fill=config.font_color)
    return np.array(img.convert("RGB"))


def _load_font(config: SubtitleConfig) -> ImageFont.ImageFont:
    """Загружает шрифт по пути; при ошибке — встроенный по умолчанию."""
    try:
        return ImageFont.truetype(config.font_path, config.font_size)
    except (OSError, IOError):
        return ImageFont.load_default(size=config.font_size)


def _compute_position(
    size: tuple[int, int], text_w: int, text_h: int, config: SubtitleConfig
) -> tuple[int, int]:
    """Вычисляет координаты (x, y) левого верхнего угла текста."""
    width, height = size
    x = (width - text_w) // 2
    if config.position == "top":
        y = config.margin
    elif config.position == "center":
        y = (height - text_h) // 2
    else:
        y = height - text_h - config.margin
    return x, y
