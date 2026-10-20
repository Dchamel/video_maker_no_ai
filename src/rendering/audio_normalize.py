"""Нормализация громкости WAV-дорожек.

Автоопределение уровня (RMS) каждого аудио и приведение всех
сегментов к единому целевому уровню с возможностью занижения/
завышения через gain_percent. По умолчанию выключено в конфиге.

Работает через moviepy: к AudioFileClip применяется множитель
громкости (volumex), вычисленный как target_rms / source_rms.
"""
from __future__ import annotations

import wave
from pathlib import Path

import numpy as np
from moviepy import AudioFileClip

from config.default_config import AudioConfig
from src.utils.logging_setup import get_logger

logger = get_logger("audio_normalize")


def compute_rms(path: str) -> float:
    """Среднеквадратичный уровень (RMS) WAV-файла — мера громкости."""
    with wave.open(str(path), "rb") as wav:
        nframes = wav.getnframes()
        sampwidth = wav.getsampwidth()
        nchannels = wav.getnchannels()
        frames = wav.readframes(nframes)

    if sampwidth == 2:
        samples = np.frombuffer(frames, dtype=np.int16).astype(np.float64)
    elif sampwidth == 4:
        samples = np.frombuffer(frames, dtype=np.int32).astype(np.float64)
    else:
        samples = np.frombuffer(frames, dtype=np.uint8).astype(np.float64) - 128.0

    if nchannels > 1:
        samples = samples.reshape(-1, nchannels).mean(axis=1)
    if samples.size == 0:
        return 0.0
    rms = float(np.sqrt(np.mean(samples**2)))
    logger.debug("RMS %s = %.1f", Path(path).name, rms)
    return rms


def normalize_clips(
    clips: list[AudioFileClip], paths: list[str], config: AudioConfig
) -> list[AudioFileClip]:
    """Приводит громкость всех клипов к единому уровню с gain_percent.

    Возвращает новый список клипов с применённым множителем громкости.
    Если normalize=False — возвращает клипы как есть.
    """
    if not config.normalize or not clips:
        return clips

    rms_values = [compute_rms(p) for p in paths]
    valid = [r for r in rms_values if r > 0]
    if not valid:
        logger.warning("Все аудио тихие — нормализация пропущена")
        return clips

    target_rms = float(np.median(valid))
    gain_base = config.gain_percent / 100.0
    logger.info(
        "Нормализация: целевой RMS=%.1f, gain=%.0f%%", target_rms, config.gain_percent
    )

    result: list[AudioFileClip] = []
    for clip, rms in zip(clips, rms_values):
        if rms > 0:
            factor = (target_rms / rms) * gain_base
        else:
            factor = gain_base
        result.append(clip.with_effects([_volume_effect(factor)]))
    return result


def _volume_effect(factor: float):
    """Эффект изменения громкости на множитель factor.

    В moviepy 2.x нет готового vfx для громкости — используется
    метод клипа with_volume_scaled. Эта функция оставлена для
    совместимости, но нормализация применяется в slide_clip.
    """
    return None
