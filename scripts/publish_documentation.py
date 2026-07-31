#!/usr/bin/env python3
"""Publish generated documentation atomically while preserving the previous known good version."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from typing import Optional


def write_to_staging_area(markdown_content: str, staging_dir: Path, target_name: str = "generated-documentation.md") -> Path:
    staging_dir.mkdir(parents=True, exist_ok=True)
    target_path = staging_dir / target_name
    target_path.write_text(markdown_content, encoding="utf-8")
    return target_path


def publish_to_canonical(staging_path: Path, docs_dir: Path, target_name: str = "generated-documentation.md") -> Path:
    docs_dir.mkdir(parents=True, exist_ok=True)
    canonical_path = docs_dir / target_name
    backup_path = docs_dir / f".{target_name}.bak"
    temp_path = docs_dir / f".{target_name}.tmp"

    try:
        if canonical_path.exists():
            shutil.copy2(canonical_path, backup_path)

        temp_path.write_text(staging_path.read_text(encoding="utf-8"), encoding="utf-8")
        os.replace(temp_path, canonical_path)

        if backup_path.exists():
            backup_path.unlink()
        return canonical_path
    except OSError as exc:
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)
        if backup_path.exists() and canonical_path.exists():
            canonical_path.unlink(missing_ok=True)
            os.replace(backup_path, canonical_path)
        raise RuntimeError(f"Failed to publish documentation: {exc}") from exc
