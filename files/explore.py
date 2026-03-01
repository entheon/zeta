"""Walk a directory tree and display every file with its size.

Usage:
    uv run python -m files.explore <root_dir>
"""

from pathlib import Path

import click

_UNITS = ("B", "KB", "MB", "GB", "TB")


def format_size(size_bytes: int) -> str:
    """Format *size_bytes* as a human-readable string (e.g. ``1.2 MB``).

    Uses base-1024 units: B, KB, MB, GB, TB.
    """
    value = float(size_bytes)
    for unit in _UNITS[:-1]:
        if abs(value) < 1024.0:
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} {unit}"
        value /= 1024.0
    return f"{value:.1f} {_UNITS[-1]}"


def _print_directory(directory: Path, files: list[Path]) -> None:
    """Display file listing for a single directory."""
    total_size = 0

    click.echo("=" * 60)
    click.echo(f"Directory: {directory}")

    for file_path in files:
        try:
            size = file_path.stat().st_size
            click.echo(f"  {file_path.name} | {format_size(size)}")
            total_size += size
        except OSError:
            click.echo(f"  {file_path.name} | (unable to read)")

    click.echo(f"Total: {format_size(total_size)}")


@click.command()
@click.argument(
    "root_dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),  # type: ignore[type-var]
)
def explore(root_dir: Path) -> None:
    """Walk ROOT_DIR and display all files with their sizes."""
    root_dir = root_dir.resolve()
    total_size = 0
    total_files = 0

    for dirpath, _, filenames in root_dir.walk():
        if filenames:
            file_paths = [dirpath / name for name in filenames]
            _print_directory(dirpath, file_paths)
            for file_path in file_paths:
                try:
                    total_size += file_path.stat().st_size
                    total_files += 1
                except OSError:
                    pass

    click.echo("=" * 60)
    click.echo(f"Grand Total: {total_files} files, {format_size(total_size)}")


if __name__ == "__main__":
    explore()
