# File-System Utilities

Tools for exploring and cleaning up directory trees.

## Commands

### Clean Empty Media Directories

Scans a directory tree for subdirectories that contain no media files
(video formats: mp4, avi, mkv, mov, etc.) and offers to delete them.

Intelligently consolidates — if a parent and all children have no media,
only the parent is suggested for deletion.

```bash
inv files.clean-empty path/to/media/
inv files.clean-empty path/to/media/ --dry-run
```

### Explore Directory

Walks a directory tree and displays every file with a human-readable size.
Shows per-directory totals and a grand total at the end.

```bash
inv files.explore path/to/dir/
```
