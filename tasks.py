from typing import Optional, cast

from invoke import Collection, Context, Task, task


@task
def categorize_passwords(
    c: Context,
    json_file: str,
    output: Optional[str] = None,
    recategorize: bool = False,
    dry_run: bool = False,
) -> None:
    """Categorize passwords using LLM and generate suggestions.

    Args:
        c: Invoke context.
        json_file: Path to Bitwarden JSON export.
        output: Output directory for report files.
        recategorize: Re-run LLM even for already-categorized entries.
        dry_run: Preview without writing output files.
    """
    args = [json_file]
    if output:
        args.append(f"--output {output}")
    if recategorize:
        args.append("--recategorize")
    if dry_run:
        args.append("--dry-run")
    c.run(f"uv run python -m modules.passwords.categorize {' '.join(args)}")


@task
def categorize_emails(
    c: Context,
    input_dir: str,
    output: Optional[str] = None,
    dry_run: bool = False,
) -> None:
    """Categorize emails using LLM and generate a filter suggestion report.

    Args:
        c: Invoke context.
        input_dir: Directory containing .metadata.json email files.
        output: Path for the output JSON results file.
        dry_run: Preview without writing output files.
    """
    args = [input_dir]
    if output:
        args.append(f"--output {output}")
    if dry_run:
        args.append("--dry-run")
    c.run(f"uv run python -m modules.emails.categorize {' '.join(args)}")


categorize_ns = Collection("categorize")
categorize_ns.add_task(cast(Task, categorize_passwords), name="passwords")
categorize_ns.add_task(cast(Task, categorize_emails), name="emails")


@task
def apply_passwords(
    c: Context,
    suggestions_file: str,
    json_file: Optional[str] = None,
    min_confidence: float = 0.4,
    dry_run: bool = False,
) -> None:
    """Apply password folder suggestions to a Bitwarden JSON export.

    Args:
        c: Invoke context.
        suggestions_file: Path to suggestions JSON from categorize.passwords.
        json_file: Override the Bitwarden JSON path from the suggestions file.
        min_confidence: Minimum confidence threshold for applying suggestions.
        dry_run: Preview changes without writing output.
    """
    args = [suggestions_file]
    if json_file:
        args.append(f"--json-file {json_file}")
    if min_confidence != 0.4:
        args.append(f"--min-confidence {min_confidence}")
    if dry_run:
        args.append("--dry-run")
    c.run(f"uv run python -m modules.passwords.apply {' '.join(args)}")


apply_ns = Collection("apply")
apply_ns.add_task(cast(Task, apply_passwords), name="passwords")


# ── PDF utilities ────────────────────────────────────────────────────────


@task(name="combine")
def pdf_combine(
    c: Context,
    pdf_dir: str,
    output: str = "combined.pdf",
    dry_run: bool = False,
) -> None:
    """Merge all PDFs in a directory into a single file.

    Args:
        c: Invoke context.
        pdf_dir: Directory containing PDF files.
        output: Output filename.
        dry_run: Show files without merging.
    """
    args = [pdf_dir]
    if output != "combined.pdf":
        args.append(f"--output {output}")
    if dry_run:
        args.append("--dry-run")
    c.run(f"uv run python -m pdf.combine {' '.join(args)}")


@task(name="images")
def pdf_images(
    c: Context,
    image_dir: str,
    output: str = "output.pdf",
    dry_run: bool = False,
) -> None:
    """Convert all images in a directory to a single PDF.

    Args:
        c: Invoke context.
        image_dir: Directory containing image files.
        output: Output filename.
        dry_run: Show files without converting.
    """
    args = [image_dir]
    if output != "output.pdf":
        args.append(f"--output {output}")
    if dry_run:
        args.append("--dry-run")
    c.run(f"uv run python -m pdf.images {' '.join(args)}")


pdf_ns = Collection("pdf")
pdf_ns.add_task(cast(Task, pdf_combine))
pdf_ns.add_task(cast(Task, pdf_images))


# ── File-system utilities ────────────────────────────────────────────────


@task(name="clean-empty")
def files_clean_empty_media(
    c: Context,
    root_dir: str,
    dry_run: bool = False,
) -> None:
    """Scan for and delete directories without media files.

    Args:
        c: Invoke context.
        root_dir: Root directory to scan.
        dry_run: Show directories without deleting.
    """
    args = [root_dir]
    if dry_run:
        args.append("--dry-run")
    c.run(f"uv run python -m files.clean_empty_media {' '.join(args)}")


@task(name="explore")
def files_explore(c: Context, root_dir: str) -> None:
    """Walk a directory tree and display every file with its size.

    Args:
        c: Invoke context.
        root_dir: Root directory to explore.
    """
    c.run(f"uv run python -m files.explore {root_dir}")


files_ns = Collection("files")
files_ns.add_task(cast(Task, files_clean_empty_media))
files_ns.add_task(cast(Task, files_explore))


# ── Development helpers ──────────────────────────────────────────────────


@task
def test(c: Context, verbose: bool = False) -> None:
    """Run the test suite with coverage.

    Args:
        c: Invoke context.
        verbose: Enable verbose pytest output.
    """
    v = "-v" if verbose else ""
    c.run(f"uv run pytest --cov {v}")


@task
def lint(c: Context) -> None:
    """Run ruff check and mypy across the entire project.

    Args:
        c: Invoke context.
    """
    c.run("uv run ruff check .")
    c.run("uv run mypy .")


@task(name="mypy")
def mypy_check(c: Context) -> None:
    """Run mypy type checking across the entire project.

    Args:
        c: Invoke context.
    """
    c.run("uv run mypy .")


@task(name="format")
def format_code(c: Context) -> None:
    """Auto-fix lint issues and format all code.

    Args:
        c: Invoke context.
    """
    c.run("uv run ruff check --fix .")
    c.run("uv run ruff format .")


@task
def warmup(c: Context) -> None:
    """Load the LLM model into memory.

    Args:
        c: Invoke context.
    """
    c.run("uv run python -m llm.warmup")


@task
def help(c: Context) -> None:
    """Print available commands and their descriptions.

    Args:
        c: Invoke context.
    """
    commands = [
        ("warmup", "Load model into memory"),
        ("categorize.passwords <json>", "Generate password suggestions"),
        ("categorize.emails <dir>", "Categorize emails + report"),
        ("apply.passwords <json>", "Apply password suggestions"),
        ("pdf.combine <dir>", "Merge PDFs in a directory"),
        ("pdf.images <dir>", "Convert images to a single PDF"),
        ("files.clean-empty <dir>", "Delete dirs without media files"),
        ("files.explore <dir>", "List files with sizes"),
        ("test", "Run test suite"),
        ("lint", "Run ruff + mypy"),
        ("mypy", "Run mypy only"),
        ("format", "Auto-fix + format code"),
        ("help", "Show this help"),
    ]
    print("\n  Zeta Commands\n")
    for cmd, desc in commands:
        print(f"  inv {cmd:<30s} {desc}")
    print()


ns = Collection()
ns.add_collection(categorize_ns)
ns.add_collection(apply_ns)
ns.add_collection(pdf_ns)
ns.add_collection(files_ns)
ns.add_task(cast(Task, warmup))
ns.add_task(cast(Task, test))
ns.add_task(cast(Task, lint))
ns.add_task(mypy_check)
ns.add_task(format_code)
ns.add_task(cast(Task, help))
