"""Directory scanning helpers for the downloads organizer."""

from pathlib import Path


def scan_directory(directory: str | Path, recursive: bool = False) -> list[Path]:
    """Return regular files found in a directory in deterministic order.

    By default, only files directly inside directory are returned.
    Set recursive=True to include files in subdirectories.

    This function never moves, modifies, or deletes files. Invalid
    directory paths raise a clear exception for the caller to handle.
    """
    root = Path(directory).expanduser()

    if not root.exists():
        raise FileNotFoundError(f"Directory does not exist: {root}")

    if not root.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {root}")

    candidates = root.rglob("*") if recursive else root.iterdir()

    return sorted(
        (path for path in candidates if path.is_file()),
        key=lambda path: str(path).casefold(),
    )
