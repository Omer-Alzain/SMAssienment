"""File type categories used by the downloads organizer."""

from pathlib import Path

CATEGORY_EXTENSIONS: dict[str, set[str]] = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".tiff"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".odt", ".rtf", ".md", ".csv"},
    "Videos": {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".webm"},
    "Audio": {".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"},
    "Programs": {".py", ".js", ".ts", ".java", ".c", ".cpp", ".html", ".css", ".php"},
}

UNKNOWN_CATEGORY = "Others"


def category_for(path: str | Path) -> str:
    """Return a category based on the final file extension.

    Extension matching is case-insensitive. Unknown or missing extensions
    are assigned to the Others category.
    """
    suffix = Path(path).suffix.lower()

    for category, extensions in CATEGORY_EXTENSIONS.items():
        if suffix in extensions:
            return category

    return UNKNOWN_CATEGORY
