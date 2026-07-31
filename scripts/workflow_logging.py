#!/usr/bin/env python3
"""Helpers for structured workflow logging and CI-visible run summaries."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def build_run_summary(
    *,
    trigger_source: str,
    processed_files: list[str],
    output_location: str,
    status: str,
    message: str,
    errors: list[str] | None = None,
    redacted_items_count: int = 0,
    validation_errors_count: int = 0,
    sections_present_count: int = 0,
    output_bytes: int = 0,
) -> dict[str, Any]:
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "trigger_source": trigger_source,
        "processed_files": processed_files,
        "output_location": output_location,
        "status": status,
        "message": message,
        "errors": errors or [],
        "summary_counts": {
            "redacted_items": redacted_items_count,
            "validation_errors": validation_errors_count,
            "sections_present": sections_present_count,
            "output_bytes": output_bytes,
        },
    }


def write_run_summary(summary: dict[str, Any], summary_path: Path) -> Path:
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary_path


def emit_ci_status(status: str, summary: dict[str, Any]) -> None:
    if status == "success":
        print(f"::notice::Documentation generation succeeded: {summary['message']}")
    else:
        print(f"::error::Documentation generation failed: {summary['message']}")

    if summary.get("errors"):
        for error in summary["errors"]:
            print(f"::error::{error}")
