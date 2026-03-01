from typing import Optional

from invoke import Collection, Context, task


@task
def categorize_passwords(
    c: Context,
    json_file: str,
    output: Optional[str] = None,
    recategorize: bool = False,
    dry_run: bool = False,
) -> None:
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
    args = [input_dir]
    if output:
        args.append(f"--output {output}")
    if dry_run:
        args.append("--dry-run")
    c.run(f"uv run python -m modules.emails.categorize {' '.join(args)}")


categorize_ns = Collection("categorize")
categorize_ns.add_task(categorize_passwords, name="passwords")  # type: ignore[arg-type]
categorize_ns.add_task(categorize_emails, name="emails")  # type: ignore[arg-type]


@task
def apply_passwords(
    c: Context,
    suggestions_file: str,
    json_file: Optional[str] = None,
    min_confidence: float = 0.4,
    dry_run: bool = False,
) -> None:
    args = [suggestions_file]
    if json_file:
        args.append(f"--json-file {json_file}")
    if min_confidence != 0.4:
        args.append(f"--min-confidence {min_confidence}")
    if dry_run:
        args.append("--dry-run")
    c.run(f"uv run python -m modules.passwords.apply {' '.join(args)}")


apply_ns = Collection("apply")
apply_ns.add_task(apply_passwords, name="passwords")  # type: ignore[arg-type]


@task
def test(c: Context, verbose: bool = False) -> None:
    v = "-v" if verbose else ""
    c.run(f"uv run pytest {v}")


@task
def lint(c: Context) -> None:
    c.run("uv run ruff check .")
    c.run("uv run mypy llm/ modules/")


@task(name="mypy")
def mypy_check(c: Context) -> None:
    c.run("uv run mypy llm/ modules/")


@task(name="format")
def format_code(c: Context) -> None:
    c.run("uv run ruff check --fix .")
    c.run("uv run ruff format .")


@task
def warmup(c: Context) -> None:
    c.run("uv run python -m llm.warmup")


@task
def help(c: Context) -> None:
    commands = [
        ("warmup", "Load model into memory"),
        ("categorize.passwords <json>", "Generate password suggestions"),
        ("categorize.emails <dir>", "Categorize emails + report"),
        ("apply.passwords <json>", "Apply password suggestions"),
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
ns.add_task(warmup)  # type: ignore[arg-type]
ns.add_task(test)  # type: ignore[arg-type]
ns.add_task(lint)  # type: ignore[arg-type]
ns.add_task(mypy_check)
ns.add_task(format_code)
ns.add_task(help)  # type: ignore[arg-type]
