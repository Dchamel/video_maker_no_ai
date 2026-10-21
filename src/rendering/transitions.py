"""Анимации переходов между слайдами — паттерн стратегии.

Важно: переходы применяются ТОЛЬКО к видеоряду. Аудио склеивается
встык без наложений — это сохраняет синхрон звука и картинки.
При padding=-duration видеоряд накладывается (переход), но аудио
не сжимается, поэтому звук не «торопится» относительно слайдов.

НAовные переходы добаваются созданием класса и регистрацией в _STRATEGIES
(Open/Closed Principle) без изменения существующего кода.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from moviepy import concatenate_audioclips, concatenate_videoclips, vfx
from moviepy.Clip import Clip


class TransitionStrategy(ABC):
    """Базовый интерфейс стратегии перехода."""

    @abstractmethod
    def apply(self, clips: list[Clip], duration: float) -> Clip:
        """Объединяет клипы с переходом заданной длительности."""


def _merge_video_audio(video: Clip, clips: list[Clip]) -> Clip:
    """Видеоряд с переходами + аудио встык без наложений.

    Аудио склеивается простой конкатенацией (method='chain'),
    чтобы длительность звука = сумма длин аудио, без сжатия.
    """
    audios = [c.audio for c in clips if c.audio is not None]
    audio = concatenate_audioclips(audios) if audios else None
    result = video.with_audio(audio) if audio is not None else video
    return result


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
        video = concatenate_videoclips(result)
        return _merge_video_audio(video, clips)


class CrossFadeTransition(TransitionStrategy):
    """Плавный переход: следующий слайд проявляется поверх предыдущего."""

    def apply(self, clips: list[Clip], duration: float) -> Clip:
        result = [clips[0]]
        for clip in clips[1:]:
            result.append(clip.with_effects([vfx.CrossFadeIn(duration)]))
        video = concatenate_videoclips(result, method="compose", padding=-duration)
        return _merge_video_audio(video, clips)


class SlideLeftTransition(TransitionStrategy):
    """Сдвиг следующего слайда справа налево поверх предыдущего."""

    def apply(self, clips: list[Clip], duration: float) -> Clip:
        result = [clips[0]]
        for clip in clips[1:]:
            result.append(clip.with_effects([vfx.SlideIn(duration, "left")]))
        video = concatenate_videoclips(result, method="compose", padding=-duration)
        return _merge_video_audio(video, clips)


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
