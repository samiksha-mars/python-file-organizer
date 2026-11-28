# Python File Organizer

A small command-line tool that sorts the files in a directory into category subfolders
(`images/`, `documents/`, `audio/`, `video/`, `code/`, etc.) based on their extension.
Uses only the Python standard library.

## Features

- Groups files by type (images, documents, spreadsheets, audio, video, archives, code)
- `--dry-run` mode to preview changes without moving anything
- Ignores hidden files
- Safe: only moves regular files, creates target folders as needed, and never overwrites
  an existing file (a clash is renamed, e.g. `photo.jpg` becomes `photo (1).jpg`)
- A file that cannot be moved is reported and skipped; the rest are still organized,
  and the exit status is 1 so scripts can notice

## Usage

```bash
# Organize the current directory
python3 file_organizer.py

# Organize a specific directory
python3 file_organizer.py ~/Downloads

# Preview without moving
python3 file_organizer.py ~/Downloads --dry-run
```

## Tests

```bash
python3 -m unittest test_file_organizer.py
```
