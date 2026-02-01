from invoke import task


@task
def passwords(c, csv_file, dry_run=False):
    args = [csv_file]
    if dry_run:
        args.append("--dry-run")
    c.run(f"uv run python -m modules.passwords.categorize {' '.join(args)}")


@task
def emails(c, input_dir, output=None, dry_run=False):
    args = [input_dir]
    if output:
        args.append(f"--output {output}")
    if dry_run:
        args.append("--dry-run")
    c.run(f"uv run python -m modules.emails.categorize {' '.join(args)}")


@task
def test(c, verbose=False):
    v = "-v" if verbose else ""
    c.run(f"uv run pytest {v}")


@task
def lint(c):
    c.run("uv run ruff check .")
    c.run("uv run mypy llm/ modules/")


@task
def format(c):
    c.run("uv run ruff check --fix .")
    c.run("uv run ruff format .")
