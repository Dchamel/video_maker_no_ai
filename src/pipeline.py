"""Общий пайплайн: scan -> match -> validate -> render.

Тонкая оркестрация без бизнес-логики. Вызывается и из main.py (CLI),
и из notebook.ipynb — единая точка запуска (DRY).
"""
from __future__ import annotations

from config.default_config import Config
from src.matcher import build_project
from src.models import Project
from src.rendering.renderer import render
from src.scanner import scan_project
from src.subtitle_parser import parse_subtitles
from src.utils.logging_setup import get_logger
from src.validator import validate

logger = get_logger("pipeline")


def run_pipeline(config: Config) -> str:
    """Полный цикл сборки видео из папки проекта. Возвращает путь к mp4."""
    logger.info("Запуск пайплайна для проекта: %s", config.project_path)

    scanned = scan_project(config.project_path)
    if scanned.txt_path:
        subtitle_blocks = parse_subtitles(scanned.txt_path)
    else:
        subtitle_blocks = {}
        logger.warning("Файл субтитров не найден — слайды без текста")

    project = build_project(scanned, subtitle_blocks, config.project_path)
    issues = validate(scanned, project)
    if issues:
        logger.warning("Обнаружены проблемы целостности (%d). Рендер продолжается.", len(issues))

    return render(project, config)
