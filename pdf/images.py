"""Convert all images in a directory into a single PDF.

Usage:
    uv run python -m pdf.images <image_dir> [--output output.pdf] [--dry-run]
"""

from pathlib import Path

import click
from PIL import Image

from pdf._sorting import natural_sort_key

IMAGE_EXTENSIONS = frozenset(
    {
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
        ".bmp",
        ".tiff",
        ".gif",
    }
)


@click.command()
@click.argument(
    "image_dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),  # type: ignore[type-var]
)
@click.option("--output", "-o", default="output.pdf", help="Output filename.")
@click.option(
    "--dry-run", is_flag=True, default=False, help="Show files without converting."
)
def images(image_dir: Path, output: str, dry_run: bool) -> None:
    """Convert all images in IMAGE_DIR to a single PDF.

    Images are sorted naturally (img_1.jpg, img_2.jpg, img_10.jpg).
    Supports: PNG, JPG, JPEG, WebP, BMP, TIFF, GIF.
    """
    image_dir = image_dir.resolve()
    image_paths = sorted(
        (p for p in image_dir.iterdir() if p.suffix.lower() in IMAGE_EXTENSIONS),
        key=lambda p: natural_sort_key(p.name),
    )

    if not image_paths:
        click.echo("No image files found in directory.")
        return

    click.echo(f"Images to convert ({len(image_paths)} files):")
    for img in image_paths:
        click.echo(f"  {img.name}")

    if dry_run:
        click.echo("\nDry run mode — no files were converted.")
        return

    output_path = image_dir / output

    if output_path.exists():
        if not click.confirm(f"\n'{output}' already exists. Overwrite?"):
            click.echo("Operation cancelled.")
            return

    opened: list[Image.Image] = []
    try:
        for path in image_paths:
            opened.append(Image.open(path).convert("RGB"))

        opened[0].save(
            str(output_path),
            "PDF",
            save_all=True,
            append_images=opened[1:],
        )

        click.echo(f"\nPDF saved: {output_path}")
    finally:
        for image in opened:
            image.close()


if __name__ == "__main__":
    images()
