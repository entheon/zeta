from pathlib import Path

import pytest
from click.testing import CliRunner

from pdf.combine import combine


@pytest.fixture
def pdf_dir(tmp_path: Path) -> Path:
    """Create a directory with small PDF files for testing.

    Generates minimal valid PDFs using pypdf so we can verify merge order
    and output correctness.
    """
    from pypdf import PdfWriter

    for name in ("doc_1.pdf", "doc_2.pdf", "doc_10.pdf"):
        writer = PdfWriter()
        writer.add_blank_page(width=72, height=72)
        writer.write(str(tmp_path / name))
        writer.close()

    return tmp_path


def test_combine_merges_in_natural_order(pdf_dir: Path) -> None:
    """Verify PDFs are merged in natural sort order and output is created."""
    runner = CliRunner()
    result = runner.invoke(combine, [str(pdf_dir)])

    assert result.exit_code == 0
    assert "3 files" in result.output
    assert "doc_1.pdf" in result.output

    output_path = pdf_dir / "combined.pdf"
    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_combine_dry_run(pdf_dir: Path) -> None:
    """Verify --dry-run lists files but does not create output."""
    runner = CliRunner()
    result = runner.invoke(combine, [str(pdf_dir), "--dry-run"])

    assert result.exit_code == 0
    assert "Dry run" in result.output
    assert not (pdf_dir / "combined.pdf").exists()


def test_combine_no_pdfs(tmp_path: Path) -> None:
    """Verify a helpful message when the directory has no PDFs."""
    runner = CliRunner()
    result = runner.invoke(combine, [str(tmp_path)])

    assert result.exit_code == 0
    assert "No PDF files found" in result.output


def test_combine_custom_output(pdf_dir: Path) -> None:
    """Verify --output writes to the specified filename."""
    runner = CliRunner()
    result = runner.invoke(combine, [str(pdf_dir), "--output", "merged.pdf"])

    assert result.exit_code == 0
    assert (pdf_dir / "merged.pdf").exists()


def test_combine_overwrite_confirmed(pdf_dir: Path) -> None:
    """Verify overwrite prompt when output already exists."""
    from pypdf import PdfWriter

    # Create a valid single-page PDF as the existing output
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    writer.write(str(pdf_dir / "combined.pdf"))
    writer.close()
    original_size = (pdf_dir / "combined.pdf").stat().st_size

    runner = CliRunner()
    # 4 PDFs now (3 originals + combined.pdf), confirm overwrite
    result = runner.invoke(combine, [str(pdf_dir)], input="y\n")

    assert result.exit_code == 0
    assert "Overwrite?" in result.output
    # Merged output should be larger than the single-page original
    assert (pdf_dir / "combined.pdf").stat().st_size > original_size


def test_combine_overwrite_cancelled(pdf_dir: Path) -> None:
    """Verify cancellation when user declines overwrite."""
    from pypdf import PdfWriter

    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    writer.write(str(pdf_dir / "combined.pdf"))
    writer.close()
    original_bytes = (pdf_dir / "combined.pdf").read_bytes()

    runner = CliRunner()
    result = runner.invoke(combine, [str(pdf_dir)], input="n\n")

    assert result.exit_code == 0
    assert "cancelled" in result.output
    assert (pdf_dir / "combined.pdf").read_bytes() == original_bytes
