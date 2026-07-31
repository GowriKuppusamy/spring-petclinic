#!/usr/bin/env python3
"""Validate generated Markdown content for sensitive values and required sections."""

from __future__ import annotations

import re
from typing import Iterable

REDACTION_TOKEN = "[REDACTED]"

SECRET_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(r"(?i)\b(?P<key>password|passwd|pwd)\b\s*[:=]\s*(?P<quote>[\"']?)(?P<value>[^\"'\s,;]+)(?P=quote)", re.MULTILINE),
        "password assignment",
    ),
    (
        re.compile(r"(?i)\b(?P<key>api[_-]?key|access[_-]?token|auth[_-]?token|client[_-]?secret|secret)\b\s*[:=]\s*(?P<quote>[\"']?)(?P<value>[^\"'\s,;]+)(?P=quote)", re.MULTILINE),
        "credential assignment",
    ),
    (
        re.compile(r"(?i)\b(?P<key>authorization|bearer)\b\s*[:=]\s*(?:(?P<prefix>bearer)\s+)?(?P<value>[^\s,;]+)", re.MULTILINE),
        "authorization token",
    ),
    (
        re.compile(r"(?i)-----begin (?:rsa|ec|openssh|dsa|pgp|private) key-----[\s\S]+?-----end (?:rsa|ec|openssh|dsa|pgp|private) key-----"),
        "private key block",
    ),
    (
        re.compile(r"(?i)\b(?:jdbc|postgres|postgresql|mysql|mongodb|redis|amqp|http|https)://[^\s]+", re.MULTILINE),
        "connection string",
    ),
]

DEFAULT_REQUIRED_SECTIONS = [
    "API Reference",
    "Setup and Installation",
    "Environment Configuration",
    "Change History",
]


def sanitize_markdown_content(markdown_content: str) -> tuple[str, list[str]]:
    """Redact a small set of obvious sensitive patterns from Markdown content."""

    sanitized_content = markdown_content
    redacted_items: list[str] = []

    for pattern, description in SECRET_PATTERNS:
        if pattern.search(sanitized_content):
            if description == "private key block":
                sanitized_content = pattern.sub("[REDACTED PRIVATE KEY]", sanitized_content)
            elif description == "connection string":
                sanitized_content = pattern.sub(REDACTION_TOKEN, sanitized_content)
            elif description == "authorization token":
                sanitized_content = pattern.sub(
                    lambda match: f"{match.group('key')}: {REDACTION_TOKEN}",
                    sanitized_content,
                )
            else:
                sanitized_content = pattern.sub(
                    lambda match: f"{match.group('key')}={REDACTION_TOKEN}",
                    sanitized_content,
                )
            redacted_items.append(description)

    return sanitized_content, redacted_items


def validate_markdown_content(markdown_content: str, required_sections: Iterable[str] | None = None) -> list[str]:
    """Validate the generated Markdown content for completeness and remaining leaks."""

    errors: list[str] = []
    required_section_names = list(required_sections or DEFAULT_REQUIRED_SECTIONS)

    if not markdown_content.strip():
        return ["Markdown content is empty."]

    for section_name in required_section_names:
        heading = f"## {section_name}"
        if heading not in markdown_content:
            errors.append(f"Missing required section: {section_name}")
            continue

        section_start = markdown_content.find(heading)
        next_heading_index = markdown_content.find("\n## ", section_start + len(heading))
        section_body = markdown_content[section_start:next_heading_index] if next_heading_index != -1 else markdown_content[section_start:]
        body_lines = [line for line in section_body.splitlines()[1:] if line.strip()]
        if not any(not line.startswith("#") for line in body_lines):
            errors.append(f"Required section has no content: {section_name}")

    for pattern, _ in SECRET_PATTERNS:
        if pattern.search(markdown_content):
            errors.append("Sensitive content remains after sanitization.")
            break

    return errors
