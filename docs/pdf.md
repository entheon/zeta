# PDF Utilities

Tools for combining and converting files into PDF format.

## Commands

### Combine PDFs

Merge all PDFs in a directory into a single file. Files are sorted naturally
(doc_1.pdf, doc_2.pdf, doc_10.pdf).

```bash
inv pdf.combine path/to/pdfs/
inv pdf.combine path/to/pdfs/ --output merged.pdf
inv pdf.combine path/to/pdfs/ --dry-run
```

### Images to PDF

Convert all images in a directory into a single PDF. Supports PNG, JPG, JPEG,
WebP, BMP, TIFF, and GIF.

```bash
inv pdf.images path/to/images/
inv pdf.images path/to/images/ --output document.pdf
inv pdf.images path/to/images/ --dry-run
```

## Dependencies

- [pypdf](https://pypdf.readthedocs.io/) — PDF merging
- [Pillow](https://pillow.readthedocs.io/) — image reading and conversion
