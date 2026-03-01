from pathlib import Path

from click.testing import CliRunner

from files.clean_empty_media import clean_empty_media


def _make_media_tree(root: Path) -> None:
    """Build a test tree with a mix of media-containing and empty dirs.

    Structure:
        root/
          has_media/          ← contains a .mp4
          empty_dir/          ← no files at all
          no_media/           ← .txt only (no media)
            nested_empty/     ← empty subdir
    """
    (root / "has_media").mkdir()
    (root / "has_media" / "video.mp4").write_bytes(b"\x00")

    (root / "empty_dir").mkdir()

    (root / "no_media").mkdir()
    (root / "no_media" / "readme.txt").write_text("hello")
    (root / "no_media" / "nested_empty").mkdir()


def test_clean_empty_finds_dirs(tmp_path: Path) -> None:
    """Verify empty branches are detected and reported."""
    _make_media_tree(tmp_path)

    runner = CliRunner()
    result = runner.invoke(clean_empty_media, [str(tmp_path), "--dry-run"])

    assert result.exit_code == 0
    assert "empty_dir" in result.output
    assert "no_media" in result.output
    assert "has_media" not in result.output
    assert "Dry run" in result.output


def test_clean_empty_consolidation(tmp_path: Path) -> None:
    """Verify parent-child consolidation — only the parent is listed."""
    _make_media_tree(tmp_path)

    runner = CliRunner()
    result = runner.invoke(clean_empty_media, [str(tmp_path), "--dry-run"])

    assert result.exit_code == 0
    # no_media is listed (parent), but nested_empty should not be separate
    assert "2 directories to delete" in result.output


def test_clean_empty_deletes(tmp_path: Path) -> None:
    """Verify actual deletion occurs when confirmed."""
    _make_media_tree(tmp_path)

    runner = CliRunner()
    result = runner.invoke(clean_empty_media, [str(tmp_path)], input="y\n")

    assert result.exit_code == 0
    assert "Successfully deleted 2 directories" in result.output
    assert not (tmp_path / "empty_dir").exists()
    assert not (tmp_path / "no_media").exists()
    assert (tmp_path / "has_media").exists()


def test_clean_empty_nothing_to_delete(tmp_path: Path) -> None:
    """Verify message when all dirs contain media."""
    (tmp_path / "good").mkdir()
    (tmp_path / "good" / "clip.mp4").write_bytes(b"\x00")

    runner = CliRunner()
    result = runner.invoke(clean_empty_media, [str(tmp_path), "--dry-run"])

    assert result.exit_code == 0
    assert "No empty media directories found" in result.output


def test_clean_empty_cancelled(tmp_path: Path) -> None:
    """Verify no deletion when user declines confirmation."""
    _make_media_tree(tmp_path)

    runner = CliRunner()
    result = runner.invoke(clean_empty_media, [str(tmp_path)], input="n\n")

    assert result.exit_code == 0
    assert "cancelled" in result.output
    assert (tmp_path / "empty_dir").exists()
    assert (tmp_path / "no_media").exists()
