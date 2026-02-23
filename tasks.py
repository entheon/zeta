from invoke import Collection, task


@task
def categorize_passwords(c, csv_file, output=None, recategorize=False, dry_run=False):
    args = [csv_file]
    if output:
        args.append(f"--output {output}")
    if recategorize:
        args.append("--recategorize")
    if dry_run:
        args.append("--dry-run")
    c.run(f"uv run python -m modules.passwords.categorize {' '.join(args)}")


@task
def categorize_emails(c, input_dir, output=None, dry_run=False):
    args = [input_dir]
    if output:
        args.append(f"--output {output}")
    if dry_run:
        args.append("--dry-run")
    c.run(f"uv run python -m modules.emails.categorize {' '.join(args)}")


categorize_ns = Collection("categorize")
categorize_ns.add_task(categorize_passwords, name="passwords")
categorize_ns.add_task(categorize_emails, name="emails")


@task
def apply_passwords(
    c, suggestions_file, csv_file=None, min_confidence=0.4, dry_run=False
):
    args = [suggestions_file]
    if csv_file:
        args.append(f"--csv-file {csv_file}")
    if min_confidence != 0.4:
        args.append(f"--min-confidence {min_confidence}")
    if dry_run:
        args.append("--dry-run")
    c.run(f"uv run python -m modules.passwords.apply {' '.join(args)}")


apply_ns = Collection("apply")
apply_ns.add_task(apply_passwords, name="passwords")


@task
def test(c, verbose=False):
    v = "-v" if verbose else ""
    c.run(f"uv run pytest {v}")


@task
def lint(c):
    c.run("uv run ruff check .")
    c.run("uv run mypy llm/ modules/")


@task(name="mypy")
def mypy_check(c):
    c.run("uv run mypy llm/ modules/")


@task(name="format")
def format_code(c):
    c.run("uv run ruff check --fix .")
    c.run("uv run ruff format .")


@task
def warmup(c):
    c.run("uv run python -m llm.warmup")


@task
def help(c):
    commands = [
        ("warmup", "Load model into memory"),
        ("categorize.passwords <csv>", "Generate password suggestions"),
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
ns.add_task(warmup)
ns.add_task(test)
ns.add_task(lint)
ns.add_task(mypy_check)
ns.add_task(format_code)
ns.add_task(help)
