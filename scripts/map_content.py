#!/usr/bin/env python3
"""Map extracted repository analysis data to documentation section templates.

This module is intentionally limited to Task T3: defining reusable mapping rules
and generating structured documentation section content from the Task T2 analysis
artifact. It does not perform Markdown rendering, file publishing, validation, or
logging.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parent.parent


def load_analysis(analysis_path: Path) -> dict[str, Any]:
    return json.loads(analysis_path.read_text(encoding="utf-8"))


def make_endpoint_summary(analysis: dict[str, Any]) -> list[dict[str, Any]]:
    summaries = []
    for controller in analysis.get("controllers", []):
        for endpoint in controller.get("endpoints", []):
            summaries.append(
                {
                    "controller": controller.get("className", "UnknownController"),
                    "method": endpoint.get("method", "GET"),
                    "path": endpoint.get("path", "/"),
                    "sourceFile": controller.get("file", "unknown"),
                }
            )
    return summaries


def build_api_section(analysis: dict[str, Any]) -> str:
    endpoints = make_endpoint_summary(analysis)
    lines = ["## API Reference", "", "The following endpoints were extracted from the repository analysis artifact."]
    for entry in endpoints:
        lines.append(f"- **{entry['method']}** `{entry['path']}` — {entry['controller']} ({entry['sourceFile']})")
    return "\n".join(lines)


def build_setup_section(analysis: dict[str, Any]) -> str:
    build_metadata = analysis.get("buildMetadata", {})
    java_version = build_metadata.get("javaVersion") or "Not available"
    lines = [
        "## Setup and Installation",
        "",
        "- Java version: " + java_version,
        "- Build metadata source: " + ", ".join(build_metadata.get("buildFiles", [])) if build_metadata.get("buildFiles") else "Not available",
        "- Run the application using the existing project build workflow.",
    ]
    return "\n".join(lines)


def build_configuration_section(analysis: dict[str, Any]) -> str:
    config_files = analysis.get("configurationFiles", [])
    lines = ["## Environment Configuration", ""]
    for config_file in config_files:
        lines.append(f"### {config_file['file']}")
        for property_entry in config_file.get("properties", []):
            lines.append(f"- `{property_entry['key']}` = `{property_entry['value']}`")
        lines.append("")
    return "\n".join(lines)


def build_changelog_section(analysis: dict[str, Any]) -> str:
    generated_at = analysis.get("generatedAt") or "Unknown"
    lines = [
        "## Change History",
        "",
        f"- Documentation mapping generated from analysis artifact at: {generated_at}",
        "- This section will be expanded by later documentation generation tasks.",
    ]
    return "\n".join(lines)


def build_mapping_payload(analysis: dict[str, Any]) -> dict[str, Any]:
    return {
        "apiReference": build_api_section(analysis),
        "setupInstructions": build_setup_section(analysis),
        "configurationDetails": build_configuration_section(analysis),
        "changelog": build_changelog_section(analysis),
        "fallbacks": {
            "missingEndpointDescription": "Endpoint description unavailable; source metadata was incomplete.",
            "missingConfigurationValue": "Configuration value unavailable; no entry was found in the analysis data.",
            "missingBuildMetadata": "Build metadata unavailable; repository analysis did not provide a value.",
        },
    }


def write_mapping_output(payload: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Map source analysis data into reusable documentation section templates")
    parser.add_argument(
        "--analysis",
        default="docs/generated/source-analysis.json",
        help="Path to the task T2 analysis artifact",
    )
    parser.add_argument(
        "--output",
        default="docs/generated/content-mapping.json",
        help="Path to write the content mapping artifact",
    )
    args = parser.parse_args()

    repo_root = repo_root_from_script()
    analysis_path = (repo_root / args.analysis).resolve()
    output_path = (repo_root / args.output).resolve()

    analysis = load_analysis(analysis_path)
    payload = build_mapping_payload(analysis)
    write_mapping_output(payload, output_path)

    print(f"Content mapping completed. Output written to {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
