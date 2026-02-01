"""Invoke tasks for zeta project."""

from invoke import task


@task
def passwords(c, csv_file, dry_run=False):
    """Categorize passwords from CSV using LLM.

    Args:
        c: Invoke context
        csv_file: Path to CSV file to categorize
        dry_run: Show categorization without writing output file
    """
    args = [csv_file]
    if dry_run:
        args.append("--dry-run")
    c.run(f"uv run python -m modules.passwords.categorize {' '.join(args)}")


@task
def emails(c, input_dir, output=None, dry_run=False):
    """Categorize emails from directory using LLM.

    Args:
        c: Invoke context
        input_dir: Directory containing email files
        output: Output file path
        dry_run: Show categorization without writing output file
    """
    args = [input_dir]
    if output:
        args.append(f"--output {output}")
    if dry_run:
        args.append("--dry-run")
    c.run(f"uv run python -m modules.emails.categorize {' '.join(args)}")


@task
def test(c, verbose=False):
    """Run pytest.

    Args:
        c: Invoke context
        verbose: Enable verbose output
    """
    v = "-v" if verbose else ""
    c.run(f"uv run pytest {v}")


@task
def lint(c):
    """Run ruff check and mypy.

    Args:
        c: Invoke context
    """
    c.run("uv run ruff check .")
    c.run("uv run mypy llm/ modules/")


@task
def format(c):
    """Format code with ruff.

    Args:
        c: Invoke context
    """
    c.run("uv run ruff check --fix .")
    c.run("uv run ruff format .")
