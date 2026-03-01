from pathlib import Path

from click.testing import CliRunner

from files.explore import explore, format_size


def test_format_size_bytes() -> None:
    """Verify formatting of small values stays in bytes."""
    assert format_size(0) == "0 B"
    assert format_size(512) == "512 B"


def test_format_size_kb() -> None:
    """Verify KB formatting."""
    assert format_size(1024) == "1.0 KB"
    assert format_size(1536) == "1.5 KB"


def test_format_size_mb() -> None:
    """Verify MB formatting."""
    assert format_size(1024 * 1024) == "1.0 MB"


def test_explore_lists_files(tmp_path: Path) -> None:
    """Verify explore outputs file names and sizes."""
    (tmp_path / "hello.txt").write_text("hello world")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "nested.txt").write_text("nested")

    runner = CliRunner()
    result = runner.invoke(explore, [str(tmp_path)])

    assert result.exit_code == 0
    assert "hello.txt" in result.output
    assert "nested.txt" in result.output
    assert "Grand Total: 2 files" in result.output


def test_explore_empty_directory(tmp_path: Path) -> None:
    """Verify explore handles an empty directory."""
    runner = CliRunner()
    result = runner.invoke(explore, [str(tmp_path)])

    assert result.exit_code == 0
    assert "Grand Total: 0 files" in result.output
