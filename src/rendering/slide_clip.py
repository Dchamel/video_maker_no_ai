"""Построение видеоклипа слайда: изображение + аудио + сменяющиеся субтитры.

Использует VideoClip с make_frame(t). Базовый кадр грузится один раз,
субтитры отрисовываются поверх по тайм-кодам. Разрешение берётся из
пресета качества (VideoConfig.width/height).
"""
from __future__ import annotations

import numpy as np
from PIL import Image
from moviepy import AudioFileClip, VideoClip

from config.default_config import AudioConfig, SubtitleConfig, VideoConfig
from src.models import Slide
from src.rendering.audio_normalize import compute_rms
from src.rendering.subtitle_overlay import draw_subtitle, select_phrase


def build_slide_clip(
    slide: Slide,
    video_config: VideoConfig,
    subtitle_config: SubtitleConfig,
    audio_config: AudioConfig,
    target_rms: float | None = None,
) -> VideoClip:
    """Создаёт клип слайда длиной в его аудио с наложением субтитров."""
    base_frame = _load_base_frame(slide.image_path, video_config)
    subtitles = slide.subtitles

    def make_frame(t: float) -> np.ndarray:
        text = select_phrase(subtitles, t)
        return draw_subtitle(base_frame, text, subtitle_config)

    clip = VideoClip(make_frame, duration=slide.duration)
    audio = AudioFileClip(slide.audio_path)
    audio = _maybe_normalize(audio, slide.audio_path, audio_config, target_rms)
    return clip.with_audio(audio).with_fps(video_config.fps)


def _maybe_normalize(
    audio: AudioFileClip,
    path: str,
    config: AudioConfig,
    target_rms: float | None,
) -> AudioFileClip:
    """Применяет нормализацию громкости, если включена."""
    if not config.normalize or target_rms is None or target_rms <= 0:
        return audio
    rms = compute_rms(path)
    if rms <= 0:
        return audio
    factor = (target_rms / rms) * (config.gain_percent / 100.0)
    return audio.with_volume_scaled(factor)


def _load_base_frame(image_path: str, video_config: VideoConfig) -> np.ndarray:
    """Загружает изображение и масштабирует под целевое разрешение."""
    img = Image.open(image_path).convert("RGB")
    img = img.resize((video_config.width, video_config.height))
    return np.array(img)
