"""Анимации переходов между слайдами — паттерн стратегии.

Каждая стратегия реализует единый интерфейс apply(clips, duration).
Новые переходы добавляются созданием класса и регистрацией в _STRATEGIES
(Open/Closed Principle) без изменения существующего кода.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from moviepy import concatenate_videoclips, vfx
from moviepy.Clip import Clip


class TransitionStrategy(ABC):
    """Базовый интерфейс стратегии перехода."""

    @abstractmethod
    def apply(self, clips: list[Clip], duration: float) -> Clip:
        """Объединяет клипы с переходом заданной длительности."""


class NoneTransition(TransitionStrategy):
    """Резкий срез без анимации."""

    def apply(self, clips: list[Clip], duration: float) -> Clip:
        return concatenate_videoclips(clips)


class FadeTransition(TransitionStrategy):
    """Затемнение в чёрный между слайдами (fade-through-black)."""

    def apply(self, clips: list[Clip], duration: float) -> Clip:
        result = []
        for i, clip in enumerate(clips):
            effects = []
            if i > 0:
                effects.append(vfx.FadeIn(duration))
            if i < len(clips) - 1:
                effects.append(vfx.FadeOut(duration))
            result.append(clip.with_effects(effects) if effects else clip)
        return concatenate_videoclips(result)


class CrossFadeTransition(TransitionStrategy):
    """Плавный переход: следующий слайд проявляется поверх предыдущего."""

    def apply(self, clips: list[Clip], duration: float) -> Clip:
        result = [clips[0]]
        for clip in clips[1:]:
            result.append(clip.with_effects([vfx.CrossFadeIn(duration)]))
        return concatenate_videoclips(result, method="compose", padding=-duration)


class SlideLeftTransition(TransitionStrategy):
    """Сдвиг следующего слайда справа налево поверх предыдущего."""

    def apply(self, clips: list[Clip], duration: float) -> Clip:
        result = [clips[0]]
        for clip in clips[1:]:
            result.append(clip.with_effects([vfx.SlideIn(duration, "left")]))
        return concatenate_videoclips(result, method="compose", padding=-duration)


_STRATEGIES: dict[str, TransitionStrategy] = {
    "none": NoneTransition(),
    "fade": FadeTransition(),
    "crossfade": CrossFadeTransition(),
    "slide_left": SlideLeftTransition(),
}


def get_transition(name: str) -> TransitionStrategy:
    """Возвращает стратегию перехода по имени."""
    if name not in _STRATEGIES:
        raise ValueError(
            f"Неизвестный переход '{name}'. Доступны: {list(_STRATEGIES)}"
        )
    return _STRATEGIES[name]
