# Smart Downloads Organizer

A Python application that scans a directory, identifies file types, and organizes files into category-based folders.

## Features

- **Directory scanning:** Finds files in a selected directory, with optional recursive scanning.
- **File categorization:** Classifies files based on their extensions.
- **Automatic organization:** Moves files into category folders.
- **Duplicate handling:** Renames duplicate files instead of overwriting existing files.
- **Dry-run mode:** Previews planned file movements without modifying the filesystem.
- **Error handling:** Reports unsuccessful operations and skips invalid sources.
- **Logging:** Records organization activities and errors.

## Project Structure

```text
SMAssienment/
├── categories.py
├── scanner.py
├── organizer.py
├── tests/
│   ├── test_categories.py
│   ├── test_scanner.py
│   └── test_organizer.py
├── .gitignore
└── README.md
```

### Main Modules

- `categories.py`: Defines supported file extensions and determines each file's category.
- `scanner.py`: Scans directories and returns discovered files.
- `organizer.py`: Handles file movement, duplicate filenames, dry-run operations, and errors.
- `tests/`: Contains automated tests for the project components.

## File Categories

| Category | Examples |
|---|---|
| Images | JPG, PNG, GIF, SVG |
| Documents | PDF, DOCX, TXT, CSV |
| Videos | MP4, MKV, AVI |
| Audio | MP3, WAV, FLAC |
| Archives | ZIP, RAR, TAR, GZ |
| Programs | PY, JS, JAVA, HTML, CSS |
| Others | Unknown or unsupported extensions |

## Requirements

- Python 3.10 or newer
- pytest for running tests

## Installation

Clone the repository:

```bash
git clone https://github.com/Omer-Alzain/SMAssienment.git
cd SMAssienment
```

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install pytest:

```bash
python -m pip install pytest
```

## Usage

The project components can be used together from a Python script:

```python
from scanner import scan_directory
from categories import category_for
from organizer import organize_files

source = "~/Downloads"
destination = "~/OrganizedDownloads"

files = scan_directory(source)

# Preview the planned operations first.
preview = organize_files(
    files,
    destination,
    category_for,
    dry_run=True
)

for operation in preview:
    print(operation)

# Execute the organization after reviewing the preview.
results = organize_files(
    files,
    destination,
    category_for,
    dry_run=False
)

for result in results:
    print(result)
```

## Running Tests

Run the automated test suite:

```bash
python -m pytest -v
```

The tests cover file categorization, directory scanning, safe file organization, duplicate handling, dry-run behavior, and error handling.

## Team Responsibilities

- **Omer:** Directory scanning and file-category detection.
- **Momen:** File organization, safe movement, duplicate handling, and organizer tests.

## License

This project was developed as part of a university assignment.
