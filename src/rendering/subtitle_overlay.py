"""Отрисовка субтитра поверх кадра через Pillow.

Отступы задаются в процентах от размеров кадра — масштабируются
под разрешение автоматически. Длинные фразы переносятся по словам
(word-wrap) до max_lines, гарантированно не выходя за границы.
Шрифт масштабируется под разрешение (база — 1080p).
"""
from __future__ import annotations

from typing import Sequence

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from config.default_config import SubtitleConfig
from src.models import SubtitlePhrase

# Базовое разрешение, для которого задан font_size в конфиге.
_BASE_HEIGHT = 1080


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
    width, height = img.size

    font = _load_font(config, height)
    max_w = _available_width(width, config)
    lines = _wrap_text(draw, text, font, max_w, config.max_lines)

    line_h = _line_height(draw, font)
    total_h = line_h * len(lines)
    x, y = _compute_block_position(width, height, total_h, config)

    pad = config.background_padding
    draw.rectangle(
        (x - pad, y - pad, x + max_w + pad, y + total_h + pad),
        fill=config.background_color,
    )
    for i, line in enumerate(lines):
        line_w = draw.textlength(line, font=font)
        draw.text(
            (x + (max_w - line_w) / 2, y + i * line_h),
            line, font=font, fill=config.font_color,
        )
    return np.array(img.convert("RGB"))


def _load_font(config: SubtitleConfig, height: int) -> ImageFont.ImageFont:
    """Шрифт, масштабированный под высоту кадра (база — 1080p)."""
    size = max(8, int(config.font_size * height / _BASE_HEIGHT))
    try:
        return ImageFont.truetype(config.font_path, size)
    except (OSError, IOError):
        return ImageFont.load_default(size=size)


def _available_width(width: int, config: SubtitleConfig) -> int:
    """Доступная ширина текста = ширина кадра минус отступы слева/справа."""
    left = int(width * config.margin_left_pct / 100)
    right = int(width * config.margin_right_pct / 100)
    return max(1, width - left - right)


def _wrap_text(
    draw: ImageDraw.ImageDraw, text: str, font, max_w: int, max_lines: int
) -> list[str]:
    """Перенос текста по словам до max_lines. Последняя строка обрезается '…'."""
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=font) <= max_w or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
            if len(lines) >= max_lines - 1:
                break
    if current:
        lines.append(current)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
    if lines and draw.textlength(lines[-1], font=font) > max_w:
        while lines[-1] and draw.textlength(lines[-1] + "…", font=font) > max_w:
            lines[-1] = lines[-1][:-1]
        lines[-1] += "…"
    return lines or [""]


def _line_height(draw: ImageDraw.ImageDraw, font) -> int:
    """Высота строки с небольшим интерлиньяжем."""
    bbox = draw.textbbox((0, 0), "Ая", font=font)
    return int((bbox[3] - bbox[1]) * 1.15)


def _compute_block_position(
    width: int, height: int, total_h: int, config: SubtitleConfig
) -> tuple[int, int]:
    """Координаты (x, y) левого верхнего угла блока текста."""
    x = int(width * config.margin_left_pct / 100)
    if config.position == "top":
        y = int(height * config.margin_top_pct / 100)
    elif config.position == "center":
        y = (height - total_h) // 2
    else:
        y = height - total_h - int(height * config.margin_bottom_pct / 100)
    return x, max(0, y)
