from pathlib import Path

import pytest
from click.testing import CliRunner
from PIL import Image

from pdf.images import images


@pytest.fixture
def image_dir(tmp_path: Path) -> Path:
    """Create a directory with small test images."""
    for name in ("img_1.png", "img_2.jpg", "img_10.png"):
        img = Image.new("RGB", (10, 10), color="red")
        img.save(tmp_path / name)
        img.close()

    return tmp_path


def test_images_converts_to_pdf(image_dir: Path) -> None:
    """Verify images are converted to a PDF in natural sort order."""
    runner = CliRunner()
    result = runner.invoke(images, [str(image_dir)])

    assert result.exit_code == 0
    assert "3 files" in result.output

    output_path = image_dir / "output.pdf"
    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_images_dry_run(image_dir: Path) -> None:
    """Verify --dry-run lists files but does not create output."""
    runner = CliRunner()
    result = runner.invoke(images, [str(image_dir), "--dry-run"])

    assert result.exit_code == 0
    assert "Dry run" in result.output
    assert not (image_dir / "output.pdf").exists()


def test_images_no_images(tmp_path: Path) -> None:
    """Verify a helpful message when the directory has no images."""
    runner = CliRunner()
    result = runner.invoke(images, [str(tmp_path)])

    assert result.exit_code == 0
    assert "No image files found" in result.output


def test_images_custom_output(image_dir: Path) -> None:
    """Verify --output writes to the specified filename."""
    runner = CliRunner()
    result = runner.invoke(images, [str(image_dir), "--output", "photos.pdf"])

    assert result.exit_code == 0
    assert (image_dir / "photos.pdf").exists()
