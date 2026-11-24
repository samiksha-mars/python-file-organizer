#!/usr/bin/env python3
"""Organize files in a directory into category subfolders by extension."""

import argparse
import shutil
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


def organize(directory: Path, dry_run: bool = False) -> list[tuple[str, str]]:
    """Move files in ``directory`` into category subfolders.

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
                shutil.move(str(item), str(target_dir / item.name))
            moved.append((item.name, category))
    return moved


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Organize files into category subfolders based on extension.")
    parser.add_argument("directory", nargs="?", default=".",
                        help="Directory to organize (default: current directory)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be moved without actually moving anything")
    args = parser.parse_args()

    moved = organize(Path(args.directory), dry_run=args.dry_run)

    if not moved:
        print("No files to organize.")
        return

    action = "would be moved" if args.dry_run else "moved"
    for name, category in moved:
        print(f"{name} -> {category}/")
    print(f"{len(moved)} file(s) {action}.")


if __name__ == "__main__":
    main()
