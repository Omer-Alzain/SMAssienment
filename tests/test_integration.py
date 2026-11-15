"""Integration tests for the complete downloads organizer workflow."""

from scanner import scan_directory
from categories import category_for
from organizer import organize_files


def test_scan_categorize_and_organize_files(tmp_path):
    source = tmp_path / "Downloads"
    destination = tmp_path / "Organized"

    source.mkdir()

    files = {
        "photo.jpg": "image content",
        "report.pdf": "document content",
        "song.mp3": "audio content",
        "unknown.xyz": "unknown content",
    }

    for filename, content in files.items():
        (source / filename).write_text(content)

    scanned_files = scan_directory(source)

    results = organize_files(
        scanned_files,
        destination,
        category_for,
        dry_run=False,
    )

    assert len(results) == len(files)
    assert all(result["status"] == "moved" for result in results)

    expected_categories = {
        "photo.jpg": "Images",
        "report.pdf": "Documents",
        "song.mp3": "Audio",
        "unknown.xyz": "Others",
    }

    for filename, category in expected_categories.items():
        organized_file = destination / category / filename

        assert organized_file.is_file()
        assert organized_file.read_text() == files[filename]
        assert not (source / filename).exists()


def test_complete_workflow_dry_run_preserves_files(tmp_path):
    source = tmp_path / "Downloads"
    destination = tmp_path / "Organized"

    source.mkdir()
    original_file = source / "photo.jpg"
    original_file.write_text("image content")

    scanned_files = scan_directory(source)

    results = organize_files(
        scanned_files,
        destination,
        category_for,
        dry_run=True,
    )

    assert len(results) == 1
    assert results[0]["status"] == "planned"
    assert original_file.is_file()
    assert original_file.read_text() == "image content"
    assert not destination.exists()


def test_complete_workflow_with_recursive_scanning(tmp_path):
    source = tmp_path / "Downloads"
    destination = tmp_path / "Organized"

    nested = source / "nested"
    nested.mkdir(parents=True)

    original_file = nested / "report.pdf"
    original_file.write_text("nested document")

    scanned_files = scan_directory(source, recursive=True)

    results = organize_files(
        scanned_files,
        destination,
        category_for,
        dry_run=False,
    )

    organized_file = destination / "Documents" / "report.pdf"

    assert len(results) == 1
    assert results[0]["status"] == "moved"
    assert organized_file.read_text() == "nested document"
    assert not original_file.exists()
