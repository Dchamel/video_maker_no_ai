"""Проверка целостности проекта и печать сводной таблицы соответствий.

Таблица выводится всегда — для визуальной проверки пользователем
того, какой слайд к какому аудио и субтитрам привязан.
"""
from __future__ import annotations

from dataclasses import dataclass

from src.models import Project
from src.scanner import ScannedFiles
from src.utils.logging_setup import get_logger
from src.utils.timecode import format_timecode

logger = get_logger("validator")


@dataclass
class ValidationIssue:
    """Одна проблема целостности, выявленная при проверке."""
    slide_number: int | None
    message: str


def validate(scanned: ScannedFiles, project: Project) -> list[ValidationIssue]:
    """Проверяет проект и печатает сводную таблицу. Возвращает список проблем."""
    issues: list[ValidationIssue] = []
    slide_numbers = {s.number for s in project.slides}

    for num in sorted(set(scanned.images) - slide_numbers):
        issues.append(ValidationIssue(num, "есть изображение, нет аудио — слайд пропущен"))
    for num in sorted(set(scanned.audios) - slide_numbers):
        issues.append(ValidationIssue(num, "есть аудио, нет изображения — слайд пропущен"))

    _check_subtitle_timing(project, issues)
    _print_summary(project, issues)
    return issues


def _check_subtitle_timing(project: Project, issues: list[ValidationIssue]) -> None:
    """Проверяет, что тайм-коды фраз не выходят за длительность аудио."""
    for slide in project.slides:
        for phrase in slide.subtitles:
            if phrase.start_time > slide.duration + 0.01:
                issues.append(ValidationIssue(
                    slide.number,
                    f"тайм-код {format_timecode(phrase.start_time)} "
                    f"за пределами аудио ({slide.duration:.1f} с)",
                ))


def _print_summary(project: Project, issues: list[ValidationIssue]) -> None:
    """Печатает сводную таблицу соответствий слайд ↔ аудио ↔ субтитры."""
    print("\n=== Сводная таблица соответствий ===")
    print(f"{'Слайд':>5} | {'Изображение':<24} | {'Аудио':<20} | {'Длит.':>7} | {'Фраз':>4}")
    print("-" * 72)
    for slide in project.slides:
        from pathlib import Path
        img = Path(slide.image_path).name
        aud = Path(slide.audio_path).name
        print(f"{slide.number:>5} | {img:<24} | {aud:<20} | {slide.duration:>6.2f}с | {len(slide.subtitles):>4}")
    print(f"\nВсего слайдов: {len(project.slides)}, "
          f"общая длительность: {project.total_duration:.2f} с")
    if issues:
        print(f"\nНайдено проблем: {len(issues)}")
        for issue in issues:
            tag = f"[Слайд {issue.slide_number}]" if issue.slide_number else "[Общее]"
            print(f"  {tag} {issue.message}")
    else:
        print("\nПроблем не найдено.")
