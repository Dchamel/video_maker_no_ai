"""Построение видеоклипа слайда: изображение + аудио + сменяющиеся субтитры.

Использует VideoClip с make_frame(t) — фундаментальная конструкция moviepy,
не зависящая от деталей API фильтров. Базовый кадр (изображение) грузится
один раз, субтитры отрисовываются поверх по тайм-кодам в момент t.
"""
from __future__ import annotations

import numpy as np
from PIL import Image
from moviepy import AudioFileClip, VideoClip

from config.default_config import SubtitleConfig, VideoConfig
from src.models import Slide
from src.rendering.subtitle_overlay import draw_subtitle, select_phrase


def build_slide_clip(
    slide: Slide, video_config: VideoConfig, subtitle_config: SubtitleConfig
) -> VideoClip:
    """Создаёт клип слайда длиной в его аудио с наложением субтитров."""
    base_frame = _load_base_frame(slide.image_path, video_config)
    subtitles = slide.subtitles

    def make_frame(t: float) -> np.ndarray:
        text = select_phrase(subtitles, t)
        return draw_subtitle(base_frame, text, subtitle_config)

    clip = VideoClip(make_frame, duration=slide.duration)
    audio = AudioFileClip(slide.audio_path)
    return clip.with_audio(audio).with_fps(video_config.fps)


def _load_base_frame(image_path: str, video_config: VideoConfig) -> np.ndarray:
    """Загружает изображение и масштабирует под целевое разрешение."""
    img = Image.open(image_path).convert("RGB")
    img = img.resize((video_config.width, video_config.height))
    return np.array(img)
