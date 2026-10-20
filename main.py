"""CLI-точка входа: запуск сборки видео из консоли.

Пример:
    python main.py --project "input/Ролик 1" --output "output/Ролик 1.mp4"
    python main.py --transition fade --transition-duration 0.7
"""
from __future__ import annotations

import argparse
import sys

from config.default_config import Config
from src.pipeline import run_pipeline


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Разбор аргументов командной строки."""
    parser = argparse.ArgumentParser(
        description="Сборка видео из слайдов (jpg) + аудио (wav) + субтитров (txt)."
    )
    parser.add_argument("--project", default=None, help="Путь к папке проекта")
    parser.add_argument("--output", default=None, help="Путь к итоговому mp4")
    parser.add_argument("--fps", type=int, default=None, help="Частота кадров")
    parser.add_argument("--width", type=int, default=None, help="Ширина видео")
    parser.add_argument("--height", type=int, default=None, help="Высота видео")
    parser.add_argument("--transition", default=None,
                        help="Тип перехода: none, fade, crossfade, slide_left")
    parser.add_argument("--transition-duration", type=float, default=None,
                        help="Длительность перехода в секундах")
    parser.add_argument("--font-size", type=int, default=None,
                        help="Размер шрифта субтитров")
    parser.add_argument("--subtitle-position", default=None,
                        help="Позиция субтитров: bottom, top, center")
    return parser.parse_args(argv)


def build_config_from_args(args: argparse.Namespace) -> Config:
    """Применяет аргументы CLI к конфигурации по умолчанию."""
    config = Config.default()
    if args.project:
        config.project_path = args.project
    if args.output:
        config.output_path = args.output
    if args.fps:
        config.video.fps = args.fps
    if args.width:
        config.video.width = args.width
    if args.height:
        config.video.height = args.height
    if args.transition:
        config.transition.type = args.transition
    if args.transition_duration:
        config.transition.duration = args.transition_duration
    if args.font_size:
        config.subtitle.font_size = args.font_size
    if args.subtitle_position:
        config.subtitle.position = args.subtitle_position
    return config


def main(argv: list[str] | None = None) -> int:
    """Точка входа CLI. Возвращает код завершения."""
    args = parse_args(argv)
    config = build_config_from_args(args)
    try:
        output = run_pipeline(config)
    except Exception as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return 1
    print(f"\nГотово: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
