#!/usr/bin/env python3
"""Organize files in a directory into category subfolders by extension."""

import argparse
import shutil
import sys
from pathlib import Path

CATEGORIES: dict[str, set[str]] = {
    "images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico"},
    "documents": {".pdf", ".doc", ".docx", ".txt", ".md", ".odt", ".rtf", ".ppt", ".pptx"},
    "spreadsheets": {".xls", ".xlsx", ".ods", ".csv"},
    "audio": {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"},
    "video": {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".webm"},
    "archives": {".zip", ".tar", ".gz", ".rar", ".7z", ".bz2"},
    "code": {".py", ".java", ".js", ".ts", ".html", ".css", ".json", ".xml", ".yml", ".yaml", ".c", ".cpp"},
}


def categorize(suffix: str) -> str:
    """Return the category name for a file suffix (unknown -> 'others')."""
    suffix = suffix.lower()
    for category, extensions in CATEGORIES.items():
        if suffix in extensions:
            return category
    return "others"


def unique_destination(target_dir: Path, name: str) -> Path:
    """Return ``target_dir / name``, adding " (1)", " (2)", ... if that path is taken."""
    destination = target_dir / name
    stem, suffix = destination.stem, destination.suffix
    counter = 1
    while destination.exists():
        destination = target_dir / f"{stem} ({counter}){suffix}"
        counter += 1
    return destination


def organize(directory: Path, dry_run: bool = False) -> list[tuple[str, str]]:
    """Move files in ``directory`` into category subfolders.

    Existing files are never overwritten: if the category folder already holds a
    file with the same name, the moved file gets a numbered name instead.

    Returns a list of ``(filename, category)`` tuples.
    """
    directory = directory.resolve()
    moved: list[tuple[str, str]] = []
    for item in directory.iterdir():
        if item.is_file() and not item.name.startswith("."):
            category = categorize(item.suffix)
            if not dry_run:
                target_dir = directory / category
                target_dir.mkdir(exist_ok=True)
                shutil.move(str(item), str(unique_destination(target_dir, item.name)))
            moved.append((item.name, category))
    return moved


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Organize files into category subfolders based on extension.")
    parser.add_argument("directory", nargs="?", default=".",
                        help="Directory to organize (default: current directory)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be moved without actually moving anything")
    args = parser.parse_args(argv)

    directory = Path(args.directory)
    if not directory.is_dir():
        parser.error(f"not a directory: {args.directory}")

    try:
        moved = organize(directory, dry_run=args.dry_run)
    except OSError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if not moved:
        print("No files to organize.")
        return 0

    action = "would be moved" if args.dry_run else "moved"
    for name, category in moved:
        print(f"{name} -> {category}/")
    print(f"{len(moved)} file(s) {action}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
