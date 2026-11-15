import logging
from pathlib import Path

from organizer import organize_files


def category_for(_path):
    return "Images"


def test_normal_file_organization_and_category_folder_creation(tmp_path):
    source_dir = tmp_path / "downloads"
    source_dir.mkdir()
    source = source_dir / "photo.jpg"
    source.write_text("image data")
    destination = tmp_path / "organized"

    results = organize_files([source], destination, category_for, dry_run=False)

    target = destination / "Images" / "photo.jpg"
    assert results[0]["status"] == "moved"
    assert results[0]["destination"] == str(target)
    assert target.read_text() == "image data"
    assert not source.exists()
    assert (destination / "Images").is_dir()


def test_dry_run_does_not_move_or_create_directories(tmp_path):
    source = tmp_path / "photo.jpg"
    source.write_text("keep me")
    destination = tmp_path / "organized"

    results = organize_files([source], destination, category_for)

    assert results[0]["status"] == "planned"
    assert source.read_text() == "keep me"
    assert not destination.exists()


def test_duplicate_names_get_incrementing_suffixes(tmp_path):
    first = tmp_path / "one"
    second = tmp_path / "two"
    first.mkdir()
    second.mkdir()
    file_one = first / "photo.jpg"
    file_two = second / "photo.jpg"
    file_one.write_text("one")
    file_two.write_text("two")
    destination = tmp_path / "organized"

    results = organize_files([file_one, file_two], destination, category_for, dry_run=False)

    assert [r["status"] for r in results] == ["moved", "moved"]
    assert (destination / "Images" / "photo.jpg").read_text() == "one"
    assert (destination / "Images" / "photo (1).jpg").read_text() == "two"


def test_existing_file_is_never_overwritten(tmp_path):
    source = tmp_path / "photo.jpg"
    source.write_text("new")
    category_dir = tmp_path / "organized" / "Images"
    category_dir.mkdir(parents=True)
    existing = category_dir / "photo.jpg"
    existing.write_text("original")

    results = organize_files([source], tmp_path / "organized", category_for, dry_run=False)

    assert results[0]["status"] == "moved"
    assert existing.read_text() == "original"
    assert (category_dir / "photo (1).jpg").read_text() == "new"
    assert not source.exists()


def test_directories_are_skipped(tmp_path):
    directory = tmp_path / "folder"
    directory.mkdir()

    results = organize_files([directory], tmp_path / "organized", category_for, dry_run=False)

    assert results[0]["status"] == "skipped"
    assert directory.is_dir()
    assert not (tmp_path / "organized").exists()


def test_filesystem_error_is_reported_and_not_reported_as_success(tmp_path, monkeypatch, caplog):
    source = tmp_path / "photo.jpg"
    source.write_text("data")
    original_open = __import__("os").open

    def failing_open(path, flags, mode=0o777):
        if Path(path).name == "photo.jpg":
            raise PermissionError("permission denied")
        return original_open(path, flags, mode)

    monkeypatch.setattr("organizer.os.open", failing_open)
    with caplog.at_level(logging.ERROR):
        results = organize_files([source], tmp_path / "organized", category_for, dry_run=False)

    assert results[0]["status"] == "error"
    assert "permission denied" in results[0]["error"]
    assert source.exists()
    assert "Could not organize" in caplog.text


def test_invalid_category_is_reported_without_creating_destination(tmp_path):
    source = tmp_path / "photo.jpg"
    source.write_text("data")

    results = organize_files([source], tmp_path / "organized", lambda _p: "../outside")

    assert results[0]["status"] == "error"
    assert not (tmp_path / "organized").exists()


def test_file_already_in_category_folder_is_not_moved_onto_itself(tmp_path):
    source = tmp_path / "organized" / "Images" / "photo.jpg"
    source.parent.mkdir(parents=True)
    source.write_text("already organized")

    results = organize_files([source], tmp_path / "organized", category_for, dry_run=False)

    assert results[0]["status"] == "skipped"
    assert source.read_text() == "already organized"
    assert list(source.parent.iterdir()) == [source]
