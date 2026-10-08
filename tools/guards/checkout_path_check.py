#!/usr/bin/env python3
"""Reject tracked paths that cannot be checked out with Windows MAX_PATH."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MAX_PATH = 260  # Includes the terminating null character on Windows.


def windows_length(value: str) -> int:
    return len(value.encode("utf-16-le")) // 2


def main() -> int:
    paths = subprocess.check_output(
        ["git", "ls-files", "-z"], cwd=REPO_ROOT
    ).decode("utf-8").split("\0")[:-1]
    failures = []
    for path in paths:
        if windows_length(path) >= MAX_PATH:
            failures.append(f"repository path exceeds MAX_PATH: {path}")
        elif any(windows_length(part) > 255 for part in Path(path).parts):
            failures.append(f"filename exceeds 255 characters: {path}")
        elif os.name == "nt" and windows_length(str(REPO_ROOT / path)) >= MAX_PATH:
            failures.append(f"checkout path exceeds MAX_PATH: {REPO_ROOT / path}")
    if failures:
        for failure in failures:
            print(f"CHECKOUT_PATH_CHECK_FAIL: {failure}")
        return 1
    longest = max((windows_length(path) for path in paths), default=0)
    print(f"CHECKOUT_PATH_CHECK_PASS files={len(paths)} longest_relative_path={longest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
