from pathlib import Path

import pytest

from categories import category_for


@pytest.mark.parametrize(
    ("filename", "expected"),
    [
        ("photo.JPG", "Images"),
        ("report.pdf", "Documents"),
        ("clip.Mp4", "Videos"),
        ("song.mp3", "Audio"),
        ("backup.ZIP", "Archives"),
        ("script.py", "Programs"),
        ("README", "Others"),
        ("unknown.xyz", "Others"),
    ],
)
def test_category_for_extension(filename: str, expected: str) -> None:
    assert category_for(Path(filename)) == expected


def test_category_for_uses_only_the_final_suffix() -> None:
    assert category_for("archive.tar.gz") == "Archives"
