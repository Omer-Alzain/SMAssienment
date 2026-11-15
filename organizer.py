"""Safe file organization helpers for Smart Downloads Organizer."""

from __future__ import annotations

import logging
import os
import shutil
from pathlib import Path
from typing import Callable, Iterable, TypedDict

logger = logging.getLogger(__name__)


class Operation(TypedDict):
    source: str
    destination: str | None
    status: str
    error: str | None


def _validate_category(category: str) -> str:
    """Return a safe, single directory name or raise ValueError."""
    if not isinstance(category, str) or not category.strip():
        raise ValueError("category_for must return a non-empty string")
    category = category.strip()
    if category in {".", ".."} or Path(category).name != category or "/" in category or "\\" in category:
        raise ValueError(f"Invalid category directory name: {category!r}")
    return category


def _available_path(directory: Path, filename: str, reserved: set[Path]) -> Path:
    """Choose a path that does not exist and is not reserved by this run."""
    candidate = directory / filename
    if not candidate.exists() and candidate not in reserved:
        return candidate

    original = Path(filename)
    index = 1
    while True:
        candidate = directory / f"{original.stem} ({index}){original.suffix}"
        if not candidate.exists() and candidate not in reserved:
            return candidate
        index += 1


def _move_without_overwrite(source: Path, destination: Path) -> None:
    """Copy to an exclusively-created destination, then remove the source.

    O_EXCL guarantees that an existing destination is never overwritten,
    including when another process creates the name after our initial check.
    """
    descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o666)
    try:
        with os.fdopen(descriptor, "wb") as target, source.open("rb") as origin:
            shutil.copyfileobj(origin, target)
            target.flush()
        shutil.copystat(source, destination)
        source.unlink()
    except Exception:
        try:
            destination.unlink(missing_ok=True)
        except OSError:
            logger.exception("Could not clean up incomplete destination %s", destination)
        raise


def organize_files(
    files: Iterable[str | os.PathLike[str]],
    destination: str | os.PathLike[str],
    category_for: Callable[[str | os.PathLike[str]], str],
    dry_run: bool = True,
) -> list[Operation]:
    """Organize files into category folders without overwriting existing files.

    Each result has source, destination, status and error keys.
    Status is one of planned, moved, skipped or error.
    Directories are skipped. In dry-run mode no directories or files are made.
    """
    destination_root = Path(destination).expanduser()
    results: list[Operation] = []
    reserved: set[Path] = set()

    for item in files:
        source = Path(item).expanduser()
        result: Operation = {
            "source": str(source),
            "destination": None,
            "status": "error",
            "error": None,
        }

        try:
            if source.is_dir():
                result["status"] = "skipped"
                result["error"] = "Source is a directory"
                logger.info("Skipping directory: %s", source)
                results.append(result)
                continue
            if not source.is_file():
                result["status"] = "skipped"
                result["error"] = "Source is not an existing regular file"
                logger.info("Skipping non-file: %s", source)
                results.append(result)
                continue

            category = _validate_category(category_for(item))
            if destination_root.exists() and not destination_root.is_dir():
                raise NotADirectoryError(f"Destination root is not a directory: {destination_root}")
            category_dir = destination_root / category
            if category_dir.exists() and not category_dir.is_dir():
                raise NotADirectoryError(f"Category destination is not a directory: {category_dir}")

            intended_path = category_dir / source.name
            if source.resolve() == intended_path.resolve(strict=False):
                result["status"] = "skipped"
                result["destination"] = str(intended_path)
                result["error"] = "Source is already in its category folder"
                logger.info("Skipping file already organized: %s", source)
                results.append(result)
                continue

            target = _available_path(category_dir, source.name, reserved)
            result["destination"] = str(target)
            if dry_run:
                result["status"] = "planned"
                reserved.add(target)
                logger.info("Would move %s -> %s", source, target)
            else:
                category_dir.mkdir(parents=True, exist_ok=True)
                target = _available_path(category_dir, source.name, reserved)
                result["destination"] = str(target)
                _move_without_overwrite(source, target)
                result["status"] = "moved"
                reserved.add(target)
                logger.info("Moved %s -> %s", source, target)
        except (OSError, ValueError, TypeError) as exc:
            result["status"] = "error"
            result["error"] = str(exc)
            logger.exception("Could not organize %s: %s", source, exc)

        results.append(result)

    return results
