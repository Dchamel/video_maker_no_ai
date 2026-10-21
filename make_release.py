"""Сборка релизного zip-архива для переноса в закрытый контур.

Запуск: python make_release.py
Создаёт dist/video_maker_no_ai_v<VERSION>.zip со строго необходимым
набором файлов для локальной установки: исходники, config, точки входа,
requirements и README. Без тестов, кэша, входных/выходных данных.

Запускается по итогам каждой итерации.
"""
from __future__ import annotations

import zipfile
from pathlib import Path

VERSION = "1.2"
ROOT = Path(".")
DIST = ROOT / "dist"

# Строго необходимый набор файлов для переноса
INCLUDE_FILES = [
    "main.py",
    "notebook.ipynb",
    "requirements.txt",
    "README.md",
    "LICENSE",
    "make_release.py",
]
INCLUDE_DIRS = ["src", "config"]
# Пустые папки-заглушки (с .gitkeep) — чтобы структура была полной
KEEP_DIRS = ["input", "output"]

EXCLUDE_SUFFIXES = {".pyc", ".pyo"}
EXCLUDE_NAMES = {"__pycache__"}


def _should_skip(path: Path) -> bool:
    if path.name in EXCLUDE_NAMES:
        return True
    if path.suffix in EXCLUDE_SUFFIXES:
        return True
    return False


def _collect_files() -> list[tuple[Path, str]]:
    """Собирает (абсолютный путь, путь в архиве) для включения."""
    result: list[tuple[Path, str]] = []
    for rel in INCLUDE_FILES:
        result.append((ROOT / rel, rel))
    for d in INCLUDE_DIRS:
        for path in (ROOT / d).rglob("*"):
            if path.is_file() and not _should_skip(path):
                result.append((path, str(path)))
    for d in KEEP_DIRS:
        result.append((ROOT / d / ".gitkeep", f"{d}/.gitkeep"))
    return result


def main() -> None:
    DIST.mkdir(exist_ok=True)
    archive = DIST / f"video_maker_no_ai_v{VERSION}.zip"
    files = _collect_files()
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
        for src, arcname in files:
            if src.exists():
                zf.write(src, arcname)
    print(f"Собран архив: {archive}")
    print(f"Файлов в архиве: {len(files)}")


if __name__ == "__main__":
    main()
