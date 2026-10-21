"""Оценка и форматирование времени рендера.

Грубая эмпирическая оценка: кадры = fps × длительность × коэффициент
зависимости от разрешения и тяжести эффектов (обводка, crossfade).
Коэффициенты подобраны по реальным замерам на Python 3.14.
"""
from __future__ import annotations

# Эмпирические коэффициенты скорости рендера (кадров в секунду)
# в зависимости от высоты кадра. Замерено на тестовом стенде.
_FPS_BY_HEIGHT: dict[int, float] = {
    360: 14.0,
    480: 11.0,
    720: 6.5,
    1080: 4.0,
    1440: 2.2,
    2160: 1.0,
}
# Замедление при обводке текста и скруглённых углах (×0.7)
_EFFECT_SLOWDOWN = 0.7


def estimate_render_seconds(total_duration: float, fps: int, height: int, has_effects: bool) -> float:
    """Оценивает время рендера в секундах по длительности и разрешению."""
    frames = fps * total_duration
    speed = _FPS_BY_HEIGHT.get(height, 4.0)
    if has_effects:
        speed *= _EFFECT_SLOWDOWN
    return frames / speed if speed > 0 else 0.0


def format_duration(seconds: float) -> str:
    """Форматирует секунды в '2 мин 30 сек' или '45 сек'."""
    seconds = max(0.0, float(seconds))
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    if minutes > 0:
        return f"{minutes} мин {secs} сек"
    return f"{secs} сек"


def estimate_range(total_duration: float, fps: int, height: int, has_effects: bool) -> tuple[float, float]:
    """Возвращает (мин, макс) оценку времени — диапазон для надёжности."""
    base = estimate_render_seconds(total_duration, fps, height, has_effects)
    return base * 0.8, base * 1.4
