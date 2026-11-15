from pathlib import Path

import run_organizer


def _run_with_inputs(monkeypatch, answers, output):
    iterator = iter(answers)
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(iterator))
    monkeypatch.setattr("builtins.print", lambda message="": output.append(str(message)))
    return run_organizer.main()


def test_preview_and_cancellation_do_not_move_files(tmp_path, monkeypatch):
    source = tmp_path / "Downloads"
    source.mkdir()
    original = source / "photo.jpg"
    original.write_text("photo")
    destination = tmp_path / "Organized"
    output = []

    result = _run_with_inputs(
        monkeypatch,
        [str(source), str(destination), "", "no"],
        output,
    )

    assert result == 0
    assert original.read_text() == "photo"
    assert not destination.exists()
    assert any("PREVIEW" in line for line in output)
    assert any("Cancelled" in line for line in output)


def test_explicit_yes_organizes_files_and_prints_summary(tmp_path, monkeypatch):
    source = tmp_path / "Downloads"
    source.mkdir()
    original = source / "report.pdf"
    original.write_text("report")
    destination = tmp_path / "Organized"
    output = []

    result = _run_with_inputs(
        monkeypatch,
        [str(source), str(destination), "n", "YES"],
        output,
    )

    organized = destination / "Documents" / "report.pdf"
    assert result == 0
    assert organized.read_text() == "report"
    assert not original.exists()
    assert any("Files moved: 1" in line for line in output)
    assert any(f"Destination: {destination}" in line for line in output)


def test_recursive_scan_handles_duplicate_filenames_safely(tmp_path, monkeypatch):
    source = tmp_path / "Downloads"
    first = source / "first"
    second = source / "second"
    first.mkdir(parents=True)
    second.mkdir()
    (first / "same.jpg").write_text("first")
    (second / "same.jpg").write_text("second")
    destination = tmp_path / "Organized"
    output = []

    result = _run_with_inputs(
        monkeypatch,
        [str(source), str(destination), "yes", "YES"],
        output,
    )

    image_dir = destination / "Images"
    assert result == 0
    assert (image_dir / "same.jpg").read_text() == "first"
    assert (image_dir / "same (1).jpg").read_text() == "second"


def test_destination_inside_source_is_rejected(tmp_path, monkeypatch):
    source = tmp_path / "Downloads"
    source.mkdir()
    output = []

    result = _run_with_inputs(
        monkeypatch,
        [str(source), str(source / "organized")],
        output,
    )

    assert result == 1
    assert any("must not be the same as" in line for line in output)
    assert not (source / "organized").exists()


def test_invalid_source_path_is_reprompted(tmp_path, monkeypatch):
    source = tmp_path / "Downloads"
    source.mkdir()
    destination = tmp_path / "Organized"
    output = []

    result = _run_with_inputs(
        monkeypatch,
        [str(tmp_path / "missing"), str(source), str(destination), "n", "no"],
        output,
    )

    assert result == 0
    assert any("does not exist" in line for line in output)
    assert not destination.exists()
