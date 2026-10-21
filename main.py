"""CLI-точка входа: запуск сборки видео из консоли.

Пример:
    python main.py --project "input/Ролик" --output "output/Ролик.mp4"
    python main.py --quality 720p --transition fade
    python main.py --normalize --gain 120
"""
from __future__ import annotations

import argparse
import sys

from config.default_config import QUALITY_PRESETS, Config
from src.pipeline import run_pipeline


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Разбор аргументов командной строки."""
    parser = argparse.ArgumentParser(
        description="Сборка видео из слайдов (jpg) + аудио (wav) + субтитров (txt)."
    )
    parser.add_argument("--project", default=None, help="Путь к папке проекта")
    parser.add_argument("--output", default=None, help="Путь к итоговому mp4")
    parser.add_argument("--quality", default=None,
                        choices=list(QUALITY_PRESETS),
                        help="Качество: 360p, 480p, 720p, 1080p, 2k, 4k")
    parser.add_argument("--fps", type=int, default=None, help="Частота кадров")
    parser.add_argument("--transition", default=None,
                        help="Тип перехода: none, fade, crossfade, slide_left")
    parser.add_argument("--transition-duration", type=float, default=None,
                        help="Длительность перехода в секундах")
    _add_subtitle_args(parser)
    _add_audio_args(parser)
    return parser.parse_args(argv)


def _add_subtitle_args(parser: argparse.ArgumentParser) -> None:
    """Аргументы субтитров."""
    parser.add_argument("--font-size", type=int, default=None,
                        help="Базовый размер шрифта (для 1080p)")
    parser.add_argument("--subtitle-position", default=None,
                        help="Позиция: bottom, top, center")
    parser.add_argument("--margin-left", type=float, default=None,
                        help="Отступ слева, %% от ширины")
    parser.add_argument("--margin-right", type=float, default=None,
                        help="Отступ справа, %% от ширины")
    parser.add_argument("--margin-bottom", type=float, default=None,
                        help="Отступ снизу, %% от высоты")
    parser.add_argument("--margin-top", type=float, default=None,
                        help="Отступ сверху, %% от высоты")
    parser.add_argument("--max-lines", type=int, default=None,
                        help="Макс. строк при переносе фразы")
    parser.add_argument("--bg-opacity", type=float, default=None,
                        help="Прозрачность фона субтитров, %% (0=нет фона, 100=непрозрачный)")
    parser.add_argument("--stroke-width", type=int, default=None,
                        help="Толщина обводки текста, px (0=без обводки)")


def _add_audio_args(parser: argparse.ArgumentParser) -> None:
    """Аргументы звука."""
    parser.add_argument("--normalize", action="store_true",
                        help="Включить выравнивание громкости")
    parser.add_argument("--gain", type=float, default=None,
                        help="Громкость в %% (100=без изменений, 120=+20%%%%)")


def build_config_from_args(args: argparse.Namespace) -> Config:
    """Применяет аргументы CLI к конфигурации по умолчанию."""
    config = Config.default()
    if args.project:
        config.project_path = args.project
    if args.output:
        config.output_path = args.output
    if args.quality:
        config.video.quality = args.quality
    if args.fps:
        config.video.fps = args.fps
    if args.transition:
        config.transition.type = args.transition
    if args.transition_duration:
        config.transition.duration = args.transition_duration
    _apply_subtitle_args(config, args)
    _apply_audio_args(config, args)
    return config


def _apply_subtitle_args(config: Config, args: argparse.Namespace) -> None:
    sub = config.subtitle
    if args.font_size:
        sub.font_size = args.font_size
    if args.subtitle_position:
        sub.position = args.subtitle_position
    if args.margin_left is not None:
        sub.margin_left_pct = args.margin_left
    if args.margin_right is not None:
        sub.margin_right_pct = args.margin_right
    if args.margin_bottom is not None:
        sub.margin_bottom_pct = args.margin_bottom
    if args.margin_top is not None:
        sub.margin_top_pct = args.margin_top
    if args.max_lines:
        sub.max_lines = args.max_lines
    if args.bg_opacity is not None:
        sub.background_opacity = args.bg_opacity
    if args.stroke_width is not None:
        sub.stroke_width = args.stroke_width


def _apply_audio_args(config: Config, args: argparse.Namespace) -> None:
    if args.normalize:
        config.audio.normalize = True
    if args.gain is not None:
        config.audio.gain_percent = args.gain


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
