"""Связывание просканированных файлов в модель Project по номеру.

Слайд создаётся только для номеров, у которых есть И изображение, И аудио.
Проблемные номера (нет пары) фиксируются и отчётываются в validator.py.
"""
from __future__ import annotations

from pathlib import Path

from src.audio_probe import get_wav_duration
from src.models import Project, Slide, SubtitlePhrase
from src.scanner import ScannedFiles
from src.utils.logging_setup import get_logger

logger = get_logger("matcher")


def build_project(
    scanned: ScannedFiles,
    subtitle_blocks: dict[int, list[SubtitlePhrase]],
    project_path: str,
) -> Project:
    """Собирает Project из найденных файлов и блоков субтитров."""
    name = Path(project_path).name
    slides: list[Slide] = []

    numbers = sorted(set(scanned.images) & set(scanned.audios))
    for number in numbers:
        audio_path = scanned.audios[number]
        duration = get_wav_duration(audio_path)
        subtitles = [p for p in subtitle_blocks.get(number, [])]
        _assign_timings(subtitles, duration)
        slides.append(
            Slide(
                number=number,
                image_path=scanned.images[number],
                audio_path=audio_path,
                audio_duration=duration,
                subtitles=subtitles,
            )
        )

    logger.info("Собрано слайдов: %d", len(slides))
    return Project(name=name, path=project_path, slides=slides)


def _assign_timings(subtitles: list[SubtitlePhrase], duration: float) -> None:
    """Назначает start/end для фраз по длительности аудио слайда.

    Фразы с явным start_time сохраняют его. Фразы без start_time (None)
    распределяются равномерно в промежутках между явными тайм-кодами
    (и от последнего явного до конца аудио).
    """
    if not subtitles:
        return
    anchors = [i for i, p in enumerate(subtitles) if p.start_time is not None]
    if not anchors:
        chunk = duration / len(subtitles)
        for i, phrase in enumerate(subtitles):
            phrase.start_time = i * chunk
            phrase.end_time = (i + 1) * chunk
        return
    _spread_before_first(subtitles, anchors[0])
    for a, b in zip(anchors, anchors[1:]):
        _spread_between(subtitles, a, b, subtitles[b].start_time)
    _spread_after_last(subtitles, anchors[-1], duration)


def _spread_before_first(subtitles: list[SubtitlePhrase], first: int) -> None:
    """Фразы до первого явного тайм-кода — равномерно от 0 до него."""
    if first == 0:
        return
    end = subtitles[first].start_time
    chunk = end / (first + 1)
    for i in range(first):
        subtitles[i].start_time = i * chunk
        subtitles[i].end_time = (i + 1) * chunk


def _spread_between(
    subtitles: list[SubtitlePhrase], a: int, b: int, end_time: float
) -> None:
    """Фразы между двумя явными тайм-кодами — равномерно."""
    gap = b - a
    if gap <= 1:
        return
    start = subtitles[a].start_time
    chunk = (end_time - start) / gap
    for k in range(1, gap):
        subtitles[a + k].start_time = start + k * chunk
        subtitles[a + k].end_time = start + (k + 1) * chunk


def _spread_after_last(
    subtitles: list[SubtitlePhrase], last: int, duration: float
) -> None:
    """Фразы после последнего явного тайм-кода — равномерно до конца аудио."""
    start = subtitles[last].start_time
    tail = len(subtitles) - last - 1
    if tail == 0:
        subtitles[last].end_time = duration
        return
    chunk = (duration - start) / (tail + 1)
    for k in range(1, tail + 1):
        subtitles[last + k].start_time = start + k * chunk
        subtitles[last + k].end_time = start + (k + 1) * chunk
    subtitles[last].end_time = start + chunk
