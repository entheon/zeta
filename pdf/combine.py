"""Merge all PDFs in a directory into a single file.

Usage:
    uv run python -m pdf.combine <pdf_dir> [--output combined.pdf] [--dry-run]
"""

from pathlib import Path

import click
from pypdf import PdfWriter

from pdf._sorting import natural_sort_key


@click.command()
@click.argument(
    "pdf_dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),  # type: ignore[type-var]
)
@click.option("--output", "-o", default="combined.pdf", help="Output filename.")
@click.option(
    "--dry-run", is_flag=True, default=False, help="Show files without merging."
)
def combine(pdf_dir: Path, output: str, dry_run: bool) -> None:
    """Merge all PDFs in PDF_DIR into a single file.

    PDFs are sorted naturally (doc_1.pdf, doc_2.pdf, doc_10.pdf).
    """
    pdf_dir = pdf_dir.resolve()
    pdfs = sorted(
        (p for p in pdf_dir.iterdir() if p.suffix.lower() == ".pdf"),
        key=lambda p: natural_sort_key(p.name),
    )

    if not pdfs:
        click.echo("No PDF files found in directory.")
        return

    click.echo(f"PDFs to merge ({len(pdfs)} files):")
    for pdf in pdfs:
        click.echo(f"  {pdf.name}")

    if dry_run:
        click.echo("\nDry run mode — no files were merged.")
        return

    output_path = pdf_dir / output

    if output_path.exists():
        if not click.confirm(f"\n'{output}' already exists. Overwrite?"):
            click.echo("Operation cancelled.")
            return

    writer = PdfWriter()
    for pdf in pdfs:
        writer.append(str(pdf))

    writer.write(str(output_path))
    writer.close()

    click.echo(f"\nMerged PDF saved: {output_path}")


if __name__ == "__main__":
    combine()
