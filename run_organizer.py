"""Interactive command-line interface for Smart Downloads Organizer."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from categories import category_for
from organizer import organize_files
from scanner import scan_directory


DEFAULT_SOURCE = Path("~/Downloads")
DEFAULT_DESTINATION = Path("~/OrganizedDownloads")


def _ask_directory(
    prompt: str,
    default: Path,
    input_fn: Callable[[str], str],
    output_fn: Callable[[str], None],
    *,
    must_exist: bool,
) -> Path:
    """Prompt until a valid source or destination directory is supplied."""
    while True:
        entered = input_fn(f"{prompt} [{default.expanduser()}]: ").strip()
        path = Path(entered).expanduser() if entered else default.expanduser()

        if must_exist:
            if not path.exists():
                output_fn(f"That directory does not exist: {path}")
                continue
            if not path.is_dir():
                output_fn(f"That path is not a directory: {path}")
                continue
        elif path.exists() and not path.is_dir():
            output_fn(f"The destination exists but is not a directory: {path}")
            continue

        return path


def _ask_yes_no(
    prompt: str,
    input_fn: Callable[[str], str],
    output_fn: Callable[[str], None],
) -> bool:
    """Ask a yes/no question, using No as the default."""
    while True:
        answer = input_fn(f"{prompt} [y/N]: ").strip().lower()
        if answer in {"", "n", "no"}:
            return False
        if answer in {"y", "yes"}:
            return True
        output_fn("Please answer Y or N.")


def _display_preview(results: list[dict], output_fn: Callable[[str], None]) -> None:
    output_fn("\nPreview (no files have been moved):")
    if not results:
        output_fn("No files to organize.")
        return

    for result in results:
        output_fn(
            f"[{result['status'].upper()}] "
            f"{result['source']} -> {result['destination'] or '(no destination)'}"
        )
        if result.get("error"):
            output_fn(f"  Details: {result['error']}")


def run_cli(
    input_fn: Callable[[str], str] | None = None,
    output_fn: Callable[[str], None] | None = None,
) -> int:
    """Run the interactive workflow. Returns 0 on normal completion."""
    input_fn = input if input_fn is None else input_fn
    output_fn = print if output_fn is None else output_fn

    output_fn("=== Smart Downloads Organizer ===")
    source = _ask_directory(
        "Source directory", DEFAULT_SOURCE, input_fn, output_fn, must_exist=True
    )
    destination = _ask_directory(
        "Destination directory",
        DEFAULT_DESTINATION,
        input_fn,
        output_fn,
        must_exist=False,
    )

    source_resolved = source.resolve()
    destination_resolved = destination.resolve()
    if destination_resolved == source_resolved or source_resolved in destination_resolved.parents:
        output_fn(
            "Invalid destination: it must not be the same as, or inside, the source directory."
        )
        return 1

    recursive = _ask_yes_no(
        "Scan subdirectories recursively?", input_fn, output_fn
    )

    try:
        files = scan_directory(source, recursive=recursive)
    except (OSError, PermissionError) as exc:
        output_fn(f"Could not scan the source directory: {exc}")
        return 1

    output_fn(f"\nFound {len(files)} file(s).")
    preview = organize_files(files, destination, category_for, dry_run=True)
    _display_preview(preview, output_fn)

    confirmation = input_fn(
        "\nType YES to organize these files. Any other input cancels: "
    ).strip()
    if confirmation != "YES":
        output_fn("Cancelled. No files were moved.")
        return 0

    results = organize_files(files, destination, category_for, dry_run=False)
    moved = sum(result["status"] == "moved" for result in results)
    skipped = sum(result["status"] == "skipped" for result in results)
    errors = sum(result["status"] == "error" for result in results)

    output_fn("\n=== Organization complete ===")
    output_fn(f"Files moved: {moved}")
    output_fn(f"Files skipped: {skipped}")
    output_fn(f"Errors: {errors}")
    output_fn(f"Destination: {destination}")
    return 0


def main() -> int:
    """CLI entry point with friendly interruption and input handling."""
    try:
        return run_cli()
    except KeyboardInterrupt:
        print("\nOperation interrupted. No further files will be processed.")
        return 130
    except EOFError:
        print("\nInput ended before the operation was confirmed. No files were moved.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
