"""Отрисовка субтитра поверх кадра через Pillow.

Отступы в процентах от кадра — масштабируются под разрешение.
Длинные фразы переносятся по словам (word-wrap) до max_lines.
Подложка облегает текст по фактической ширине строк (не на всю ширину).
Прозрачность подложки и обводка текста настраиваются отдельно.
Шрифт масштабируется под разрешение (база — 1080p).
"""
from __future__ import annotations

from typing import Sequence

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from config.default_config import SubtitleConfig
from src.models import SubtitlePhrase

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
    base = Image.fromarray(frame).convert("RGBA")
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")
    width, height = base.size

    font = _load_font(config, height)
    max_w = _available_width(width, config)
    lines = _wrap_text(draw, text, font, max_w, config.max_lines)

    line_h = _line_height(draw, font)
    total_h = line_h * len(lines)
    block_w = max(draw.textlength(line, font=font) for line in lines)
    x, y = _compute_block_position(width, height, total_h, block_w, config)

    _draw_background(draw, x, y, block_w, total_h, config)
    _draw_text_lines(draw, lines, x, y, line_h, block_w, font, config)
    result = Image.alpha_composite(base, overlay)
    return np.array(result.convert("RGB"))


def _draw_background(
    draw: ImageDraw.ImageDraw, x: int, y: int, w: float, h: int, config: SubtitleConfig
) -> None:
    """Полупрозрачная подложка под текстом по фактической ширине блока."""
    if config.background_opacity <= 0:
        return
    alpha = int(255 * config.background_opacity / 100.0)
    r, g, b = config.background_color
    pad = config.background_padding
    radius = min(pad * 2, int(h / 2), int(w / 2))
    draw.rounded_rectangle(
        (x - pad, y - pad, x + w + pad, y + h + pad),
        radius=radius, fill=(r, g, b, alpha),
    )


def _draw_text_lines(
    draw: ImageDraw.ImageDraw, lines: list[str], x: int, y: int,
    line_h: int, block_w: float, font, config: SubtitleConfig,
) -> None:
    """Рисует строки по центру блока с обводкой для читаемости."""
    for i, line in enumerate(lines):
        line_w = draw.textlength(line, font=font)
        cx = x + (block_w - line_w) / 2
        cy = y + i * line_h
        if config.stroke_width > 0:
            sr, sg, sb = config.stroke_color
            draw.text(
                (cx, cy), line, font=font, fill=config.font_color,
                stroke_width=config.stroke_width, stroke_fill=(sr, sg, sb),
            )
        else:
            draw.text((cx, cy), line, font=font, fill=config.font_color)


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
    width: int, height: int, total_h: int, block_w: float, config: SubtitleConfig
) -> tuple[int, int]:
    """Координаты (x, y) левого верхнего угла блока текста."""
    x = int((width - block_w) / 2)
    if config.position == "top":
        y = int(height * config.margin_top_pct / 100)
    elif config.position == "center":
        y = (height - total_h) // 2
    else:
        y = height - total_h - int(height * config.margin_bottom_pct / 100)
    return x, max(0, y)
