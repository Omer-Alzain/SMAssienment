from pathlib import Path

import pytest

from scanner import scan_directory


def test_scan_directory_returns_files_only(tmp_path: Path) -> None:
    (tmp_path / "notes.txt").write_text("notes")
    (tmp_path / "photo.png").write_text("image")
    (tmp_path / "folder").mkdir()

    result = scan_directory(tmp_path)

    assert result == [tmp_path / "notes.txt", tmp_path / "photo.png"]


def test_scan_directory_is_non_recursive_by_default(tmp_path: Path) -> None:
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "inside.txt").write_text("inside")
    (tmp_path / "outside.txt").write_text("outside")

    assert scan_directory(tmp_path) == [tmp_path / "outside.txt"]


def test_scan_directory_can_scan_recursively(tmp_path: Path) -> None:
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "inside.txt").write_text("inside")
    (tmp_path / "outside.txt").write_text("outside")

    assert scan_directory(tmp_path, recursive=True) == [
        tmp_path / "nested" / "inside.txt",
        tmp_path / "outside.txt",
    ]


def test_scan_directory_raises_for_missing_path(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Directory does not exist"):
        scan_directory(tmp_path / "missing")


def test_scan_directory_raises_for_file_path(tmp_path: Path) -> None:
    file_path = tmp_path / "file.txt"
    file_path.write_text("content")

    with pytest.raises(NotADirectoryError, match="Path is not a directory"):
        scan_directory(file_path)
