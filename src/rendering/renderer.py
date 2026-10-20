"""Оркестрация сборки: клипы слайдов + переходы + экспорт в mp4."""
from __future__ import annotations

from pathlib import Path

import numpy as np

from config.default_config import Config
from src.models import Project
from src.rendering.audio_normalize import compute_rms
from src.rendering.slide_clip import build_slide_clip
from src.rendering.transitions import get_transition
from src.utils.logging_setup import get_logger

logger = get_logger("renderer")


def render(project: Project, config: Config) -> str:
    """Собирает все слайды в итоговое видео и сохраняет по config.output_path."""
    if not project.slides:
        raise ValueError("Нет слайдов для рендеринга")

    _ensure_ffmpeg()
    target_rms = _compute_target_rms(project, config)

    clips = [
        build_slide_clip(
            slide, config.video, config.subtitle, config.audio, target_rms
        )
        for slide in project.slides
    ]
    logger.info("Построено клипов: %d", len(clips))

    transition = get_transition(config.transition.type)
    final = transition.apply(clips, config.transition.duration)

    output_path = Path(config.output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    final.write_videofile(
        str(output_path),
        fps=config.video.fps,
        codec=config.video.codec,
        audio_codec="aac",
    )
    logger.info("Видео сохранено: %s", output_path)
    return str(output_path)


def _ensure_ffmpeg() -> None:
    """Настраивает путь к FFmpeg из imageio-ffmpeg для оффлайн-работы."""
    try:
        import imageio_ffmpeg
        from moviepy.config import Config as MoviepyConfig
        MoviepyConfig.FFMPEG_BINARY = imageio_ffmpeg.get_ffmpeg_exe()
        logger.debug("FFmpeg из imageio-ffmpeg: %s", MoviepyConfig.FFMPEG_BINARY)
    except Exception:
        logger.debug("Используется системный FFmpeg")


def _compute_target_rms(project: Project, config: Config) -> float | None:
    """Медианный RMS всех аудио — целевой уровень для нормализации.

    Возвращает None, если нормализация выключена или нет валидных аудио.
    """
    if not config.audio.normalize:
        return None
    rms_values = [compute_rms(s.audio_path) for s in project.slides]
    valid = [r for r in rms_values if r > 0]
    if not valid:
        return None
    target = float(np.median(valid))
    logger.info(
        "Целевой RMS=%.1f, gain=%.0f%%", target, config.audio.gain_percent
    )
    return target
