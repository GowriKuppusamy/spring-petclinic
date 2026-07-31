#!/usr/bin/env python3
"""Render mapped documentation content into Markdown and publish it to the canonical docs location.

This module is intentionally limited to Task T4: taking the Task T3 content mapping
artifact, assembling Markdown content, and writing it to a staging area before
publishing to the canonical docs output location. It does not implement validation,
rollback, logging, or later workflow concerns.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from publish_documentation import publish_to_canonical, write_to_staging_area
from validate_markdown import sanitize_markdown_content, validate_markdown_content


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parent.parent


def load_mapping(mapping_path: Path) -> dict[str, Any]:
    return json.loads(mapping_path.read_text(encoding="utf-8"))


def build_markdown_document(mapping: dict[str, Any]) -> str:
    title = "# Automated Documentation Sync"
    intro = "\nThis document is generated from the repository analysis and content mapping artifacts."
    sections = [
        mapping.get("apiReference", "## API Reference\n\nNo API reference content was provided."),
        mapping.get("setupInstructions", "## Setup and Installation\n\nNo setup instructions were provided."),
        mapping.get("configurationDetails", "## Environment Configuration\n\nNo configuration details were provided."),
        mapping.get("changelog", "## Change History\n\nNo changelog content was provided."),
    ]
    return "\n\n".join([title, intro, *sections]) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Render mapped content into Markdown and publish it to the canonical docs location")
    parser.add_argument(
        "--mapping",
        default="docs/generated/content-mapping.json",
        help="Path to the Task T3 content mapping artifact",
    )
    parser.add_argument(
        "--staging-dir",
        default="docs/.staging",
        help="Path to the staging directory used before publishing",
    )
    parser.add_argument(
        "--docs-dir",
        default="docs",
        help="Canonical docs output directory",
    )
    args = parser.parse_args()

    repo_root = repo_root_from_script()
    mapping_path = (repo_root / args.mapping).resolve()
    staging_dir = (repo_root / args.staging_dir).resolve()
    docs_dir = (repo_root / args.docs_dir).resolve()

    try:
        mapping = load_mapping(mapping_path)
        markdown_content = build_markdown_document(mapping)
        sanitized_content, redacted_items = sanitize_markdown_content(markdown_content)
        validation_errors = validate_markdown_content(sanitized_content)
        if validation_errors:
            raise ValueError("Documentation validation failed:\n- " + "\n- ".join(validation_errors))

        if redacted_items:
            print(f"Redacted sensitive values: {', '.join(redacted_items)}")

        staged_path = write_to_staging_area(sanitized_content, staging_dir)
        published_path = publish_to_canonical(staged_path, docs_dir)
    except (RuntimeError, ValueError) as exc:
        print(f"Publication failed: {exc}", file=sys.stderr)
        return 1

    print(f"Markdown generation completed. Staged at {staged_path}")
    print(f"Published to {published_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
