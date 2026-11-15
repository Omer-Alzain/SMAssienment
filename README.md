# Smart Downloads Organizer

A Python command-line application that scans a directory, identifies file types, and organizes files into category-based folders. It provides an interactive workflow with a preview and requires confirmation before moving files.

## Features

- **Interactive command-line interface:** Run the application without writing or editing Python code.
- **Directory scanning:** Finds files in a selected directory, with optional recursive scanning.
- **File categorization:** Classifies files based on their extensions.
- **Automatic organization:** Moves files into category folders.
- **Duplicate handling:** Renames duplicate files instead of overwriting existing files.
- **Preview before changes:** Displays planned file movements without modifying the filesystem.
- **Confirmation:** Files are moved only after the user types `YES`.
- **Path validation:** Checks the source and destination and prevents using the source itself or a directory inside it as the destination.
- **Error handling and logging:** Reports unsuccessful operations and records organizer activities and errors.

## Project Structure

```text
SMAssienment/
├── categories.py
├── scanner.py
├── organizer.py
├── run_organizer.py
├── tests/
│   ├── test_categories.py
│   ├── test_scanner.py
│   ├── test_organizer.py
│   ├── test_integration.py
│   └── test_cli.py
├── .gitignore
└── README.md
```

### Main Modules

- `categories.py`: Defines supported file extensions and determines each file's category.
- `scanner.py`: Scans directories and returns discovered files.
- `organizer.py`: Handles file movement, duplicate filenames, dry-run operations, and errors.
- `run_organizer.py`: Provides the interactive command-line application.
- `tests/`: Contains automated tests for categorization, scanning, organizing, integration, and the command-line workflow.

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
- pytest (only needed to run the tests)

## Installation

Clone the repository:

```bash
git clone https://github.com/Omer-Alzain/SMAssienment.git
cd SMAssienment
```

Create and activate a virtual environment:

**Linux / macOS**

```bash
python -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell)**

```powershell
python -m venv .venv
.venv\\Scripts\\Activate.ps1
```

Install pytest if you want to run the test suite:

```bash
python -m pip install pytest
```

The organizer itself uses Python's standard library and does not require additional packages.

## Usage

From the repository root, run:

```bash
python run_organizer.py
```

The application will guide you through these steps:

1. **Choose the source directory.** Enter the directory to organize, or press Enter to use the default `~/Downloads`.
2. **Choose the destination directory.** Enter where organized files should go, or press Enter to use `~/OrganizedDownloads`.
3. **Choose recursive scanning.** Enter `y` to include files in subdirectories, or press Enter to scan only the selected directory.
4. **Review the preview.** The application lists each planned operation. No files have been moved at this stage.
5. **Confirm the operation.** Type `YES` exactly to proceed. Any other input cancels the operation.

After organization, the application displays the number of files moved, skipped, and affected by errors, along with the destination directory.

### Example

```text
=== Smart Downloads Organizer ===
Source directory [/home/user/Downloads]:
Destination directory [/home/user/OrganizedDownloads]:
Scan subdirectories recursively? [y/N]: n

Found 3 file(s).

Preview (no files have been moved):
[PLANNED] /home/user/Downloads/photo.jpg -> /home/user/OrganizedDownloads/Images/photo.jpg
[PLANNED] /home/user/Downloads/report.pdf -> /home/user/OrganizedDownloads/Documents/report.pdf
[PLANNED] /home/user/Downloads/song.mp3 -> /home/user/OrganizedDownloads/Audio/song.mp3

Type YES to organize these files. Any other input cancels: YES

=== Organization complete ===
Files moved: 3
Files skipped: 0
Errors: 0
Destination: /home/user/OrganizedDownloads
```

The example paths and file counts are illustrative; your output depends on the files in your selected directory.

### Safety Notes

- Always review the preview before confirming.
- The application does not overwrite existing files. Duplicate names receive a numbered suffix, such as `photo (1).jpg`.
- The destination cannot be the same as the source directory or a directory inside it.
- If you are unsure, test with a temporary folder containing copies of your files first.
- Press Ctrl+C to interrupt the application.

## Using the Python Modules Directly

The modules can also be used programmatically from another Python script:

```python
from scanner import scan_directory
from categories import category_for
from organizer import organize_files

source = "~/Downloads"
destination = "~/OrganizedDownloads"

files = scan_directory(source)

# Preview planned operations without moving files.
preview = organize_files(
    files,
    destination,
    category_for,
    dry_run=True,
)

for operation in preview:
    print(operation)

# Execute only after reviewing the preview.
results = organize_files(
    files,
    destination,
    category_for,
    dry_run=False,
)

for result in results:
    print(result)
```

## Running Tests

Run the full automated test suite from the repository root:

```bash
python -m pytest -v
```

The current suite contains **30 tests** covering file categorization, directory scanning, safe organization, duplicate handling, dry-run behavior, integration, and the interactive command-line workflow.

## Team Responsibilities

- **Omer:** Directory scanning and file-category detection.
- **Momen:** File organization, safe movement, duplicate handling, and the interactive command-line interface.

## License

This project was developed as part of a university assignment.
