"""Scan for and delete directories that contain no media files.

Usage:
    uv run python -m files.clean_empty_media <root_dir> [--dry-run]
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path

import click

MEDIA_EXTENSIONS: frozenset[str] = frozenset(
    {
        ".mp4",
        ".avi",
        ".mkv",
        ".mov",
        ".wmv",
        ".flv",
        ".webm",
        ".m4v",
        ".mpg",
        ".mpeg",
        ".3gp",
        ".ts",
        ".mts",
        ".m2ts",
        ".vob",
        ".ogv",
    }
)


@dataclass
class DirectoryNode:
    """A node in the directory tree, tracking whether it contains media."""

    path: Path
    has_direct_media: bool = False
    children: dict[str, DirectoryNode] = field(default_factory=dict)
    parent: DirectoryNode | None = None

    @property
    def has_any_media(self) -> bool:
        """Return True if this node or any descendant contains media files."""
        if self.has_direct_media:
            return True
        return any(child.has_any_media for child in self.children.values())

    @property
    def is_empty(self) -> bool:
        """Return True if the directory has no entries on disk."""
        if not self.path.exists():
            return True
        return not any(self.path.iterdir())


def _has_media_files(directory: Path) -> bool:
    """Check whether *directory* directly contains any media files."""
    try:
        return any(
            p.is_file() and p.suffix.lower() in MEDIA_EXTENSIONS
            for p in directory.iterdir()
        )
    except (OSError, PermissionError):
        return False


def build_directory_tree(root: Path) -> DirectoryNode:
    """Walk *root* and build a tree annotated with media presence."""
    root_node = DirectoryNode(path=root, has_direct_media=_has_media_files(root))

    def _build(node: DirectoryNode) -> None:
        try:
            for child_path in sorted(node.path.iterdir()):
                if child_path.is_dir():
                    child_node = DirectoryNode(
                        path=child_path,
                        has_direct_media=_has_media_files(child_path),
                        parent=node,
                    )
                    node.children[child_path.name] = child_node
                    _build(child_node)
        except (OSError, PermissionError):
            pass

    _build(root_node)
    return root_node


def find_empty_branches(node: DirectoryNode, results: list[DirectoryNode]) -> None:
    """Collect subtrees that contain no media files at any depth."""
    if not node.has_any_media:
        results.append(node)
        return

    for child in node.children.values():
        find_empty_branches(child, results)


def consolidate_deletions(candidates: list[DirectoryNode]) -> list[DirectoryNode]:
    """Remove children whose parent is already scheduled for deletion."""
    if not candidates:
        return []

    candidate_paths = {node.path for node in candidates}
    consolidated: list[DirectoryNode] = []

    for node in candidates:
        ancestor = node.parent
        is_redundant = False
        while ancestor is not None:
            if ancestor.path in candidate_paths:
                is_redundant = True
                break
            ancestor = ancestor.parent

        if not is_redundant:
            consolidated.append(node)

    return consolidated


def _count_subdirs(node: DirectoryNode) -> int:
    """Count total subdirectories (recursive) under *node*."""
    count = len(node.children)
    for child in node.children.values():
        count += _count_subdirs(child)
    return count


def _deletion_reason(node: DirectoryNode) -> str:
    """Return a human-readable reason why *node* is marked for deletion."""
    if node.is_empty:
        return "Empty directory"

    subdir_count = _count_subdirs(node)
    if subdir_count > 0:
        return f"No media in tree ({subdir_count} subdirs)"
    return "No media files"


@click.command()
@click.argument(
    "root_dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),  # type: ignore[type-var]
)
@click.option(
    "--dry-run", is_flag=True, default=False, help="Show dirs without deleting."
)
def clean_empty_media(root_dir: Path, dry_run: bool) -> None:
    """Scan ROOT_DIR for directories without media files and delete them.

    Intelligently consolidates suggestions — if a parent and all children
    have no media, only the parent is suggested for deletion.
    """
    root_dir = root_dir.resolve()
    tree = build_directory_tree(root_dir)

    candidates: list[DirectoryNode] = []
    for child in tree.children.values():
        find_empty_branches(child, candidates)

    consolidated = consolidate_deletions(candidates)

    if not consolidated:
        click.echo("No empty media directories found.")
        return

    click.echo(f"Found {len(consolidated)} directories to delete:")
    for node in consolidated:
        reason = _deletion_reason(node)
        click.echo(f"  {node.path} — {reason}")

    if dry_run:
        click.echo("\nDry run mode — no directories were deleted.")
        return

    if not click.confirm(f"\nProceed with deleting {len(consolidated)} directories?"):
        click.echo("Operation cancelled.")
        return

    deleted_count = 0
    for node in consolidated:
        try:
            if node.path.exists():
                shutil.rmtree(node.path)
                click.echo(f"Deleted: {node.path}")
                deleted_count += 1
        except OSError as exc:
            click.echo(f"Error deleting {node.path}: {exc}", err=True)

    click.echo(f"\nSuccessfully deleted {deleted_count} directories.")


if __name__ == "__main__":
    clean_empty_media()
