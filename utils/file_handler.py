"""
File handling utility for secure file I/O.

Provides path validation and safe file reading with size limits.
"""
from __future__ import annotations

import os

# Anchored to the project root (parent of utils/), not the process cwd
SAFE_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def _validate_path(filepath: str) -> str:
    """Resolve *filepath* to an absolute path and verify it lives under SAFE_BASE_DIR.

    Returns the resolved absolute path on success.

    Raises:
        ValueError: If the resolved path falls outside the allowed project directory.
    """
    resolved: str = os.path.abspath(filepath)
    # Use os.path.commonpath for a true directory-boundary check.
    # startswith() alone is bypassable: SAFE_BASE_DIR + "-malicious/file"
    # would pass a string prefix test but is outside the project.
    try:
        common = os.path.commonpath([resolved, SAFE_BASE_DIR])
    except ValueError:
        # Windows: paths on different drives have no common path
        common = ""
    if common != SAFE_BASE_DIR:
        raise ValueError(
            f"Unsafe file path: '{filepath}' is outside the allowed directory."
        )
    return resolved


def read_file(path: str) -> str:
    """Read a UTF-8 text file after validating its path and checking its size.

    Args:
        path: Filesystem path (absolute or relative) to the file to read.

    Returns:
        The full contents of the file as a string.

    Raises:
        ValueError: Propagated from ``_validate_path`` when the path is unsafe.
        SystemExit: When the file does not exist or exceeds *MAX_FILE_SIZE*.
    """
    resolved_path: str = _validate_path(path)

    try:
        size: int = os.path.getsize(resolved_path)
    except FileNotFoundError:
        raise SystemExit(
            f"Error: File '{path}' not found.\n"
            "   Hint: Check the path and try again."
        )

    if size > MAX_FILE_SIZE:
        raise SystemExit(
            f"Error: File '{path}' is too large (>10 MB).\n"
            "   Hint: Use a smaller flashcard file."
        )

    try:
        with open(resolved_path, encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        raise SystemExit(
            f"Error: File '{path}' not found.\n"
            "   Hint: Check the path and try again."
        )
