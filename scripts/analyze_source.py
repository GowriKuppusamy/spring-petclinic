#!/usr/bin/env python3
"""Analyze repository source and configuration for documentation purposes.

This module is intentionally limited to Task T2: extracting documentation-relevant
information from Spring PetClinic controller classes, configuration files, and build
metadata. It does not implement generation, validation, or publishing.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ANNOTATION_NAMES = {
    "GET": "GetMapping",
    "POST": "PostMapping",
    "PUT": "PutMapping",
    "DELETE": "DeleteMapping",
    "PATCH": "PatchMapping",
}


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parent.parent


def relative_to_repo(path: Path, repo_root: Path) -> str:
    return path.relative_to(repo_root).as_posix()


def extract_class_level_paths(text: str) -> list[str]:
    lines = text.splitlines()
    collected_annotations: list[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("@RequestMapping"):
            collected_annotations.append(stripped)
            continue
        if stripped.startswith("class "):
            break
        if stripped.startswith("@"):
            continue

    paths: list[str] = []
    for annotation_line in collected_annotations:
        paths.extend(extract_paths_from_annotation(annotation_line))
    return paths


def extract_paths_from_annotation(annotation_text: str) -> list[str]:
    matches = re.findall(r"['\"]([^'\"]+)['\"]", annotation_text)
    if matches:
        return matches

    path_matches = re.findall(r"(?:value|path)\s*=\s*['\"]([^'\"]+)['\"]", annotation_text)
    return path_matches


def join_paths(base_path: str | None, method_path: str) -> str:
    if not base_path:
        return method_path
    if method_path.startswith("http://") or method_path.startswith("https://"):
        return method_path
    if method_path.startswith("/"):
        return f"{base_path.rstrip('/')}{method_path}"
    return f"{base_path.rstrip('/')}/{method_path}"


def extract_endpoints_from_controller(file_path: Path, repo_root: Path) -> dict[str, Any]:
    text = file_path.read_text(encoding="utf-8")
    class_name_match = re.search(r"class\s+(\w+)", text)
    class_name = class_name_match.group(1) if class_name_match else file_path.stem
    class_paths = extract_class_level_paths(text)
    base_path = class_paths[0] if class_paths else None

    endpoint_entries: list[dict[str, str]] = []
    for method_name, annotation_name in ANNOTATION_NAMES.items():
        for match in re.finditer(rf"@{annotation_name}\s*\((.*?)\)", text, re.DOTALL):
            paths = extract_paths_from_annotation(match.group(1))
            for path in paths:
                endpoint_entries.append(
                    {
                        "method": method_name,
                        "path": join_paths(base_path, path),
                    }
                )

    return {
        "file": relative_to_repo(file_path, repo_root),
        "className": class_name,
        "basePath": base_path,
        "endpoints": endpoint_entries,
    }


def discover_controller_files(repo_root: Path) -> list[Path]:
    java_root = repo_root / "src" / "main" / "java"
    if not java_root.exists():
        return []

    controller_files: list[Path] = []
    for file_path in java_root.rglob("*.java"):
        text = file_path.read_text(encoding="utf-8")
        if "@Controller" in text or "@RestController" in text or file_path.name.endswith("Controller.java"):
            controller_files.append(file_path)
    return sorted(controller_files)


def extract_configuration_files(repo_root: Path) -> list[dict[str, Any]]:
    resources_root = repo_root / "src" / "main" / "resources"
    if not resources_root.exists():
        return []

    entries: list[dict[str, Any]] = []
    for file_path in sorted(resources_root.glob("application*.properties")):
        properties: list[dict[str, str]] = []
        for line_number, line in enumerate(file_path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if "=" in stripped:
                key, value = stripped.split("=", 1)
                properties.append({"key": key.strip(), "value": value.strip(), "line": line_number})
        entries.append({"file": relative_to_repo(file_path, repo_root), "properties": properties})
    return entries


def extract_build_metadata(repo_root: Path) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "buildFiles": [],
        "javaVersion": None,
        "artifact": None,
        "group": None,
    }

    pom_path = repo_root / "pom.xml"
    if pom_path.exists():
        metadata["buildFiles"].append(relative_to_repo(pom_path, repo_root))
        pom_text = pom_path.read_text(encoding="utf-8")
        java_match = re.search(r"<java\.version>([^<]+)</java\.version>", pom_text)
        if java_match:
            metadata["javaVersion"] = java_match.group(1).strip()
        artifact_match = re.search(r"<artifactId>([^<]+)</artifactId>", pom_text)
        group_match = re.search(r"<groupId>([^<]+)</groupId>", pom_text)
        if artifact_match:
            metadata["artifact"] = artifact_match.group(1).strip()
        if group_match:
            metadata["group"] = group_match.group(1).strip()

    gradle_path = repo_root / "build.gradle"
    if gradle_path.exists():
        metadata["buildFiles"].append(relative_to_repo(gradle_path, repo_root))
        gradle_text = gradle_path.read_text(encoding="utf-8")
        java_match = re.search(r"languageVersion\s*=\s*JavaLanguageVersion\.of\((\d+)\)", gradle_text)
        if java_match:
            metadata["javaVersion"] = java_match.group(1).strip()
        artifact_match = re.search(r"group\s*=\s*'([^']+)'", gradle_text)
        if artifact_match:
            metadata["group"] = artifact_match.group(1).strip()

    return metadata


def build_analysis_payload(repo_root: Path) -> dict[str, Any]:
    controller_files = discover_controller_files(repo_root)
    controllers = [extract_endpoints_from_controller(file_path, repo_root) for file_path in controller_files]
    configuration_files = extract_configuration_files(repo_root)
    build_metadata = extract_build_metadata(repo_root)

    return {
        "generatedAt": "",
        "repository": {
            "name": repo_root.name,
            "root": relative_to_repo(repo_root, repo_root),
        },
        "controllers": controllers,
        "configurationFiles": configuration_files,
        "buildMetadata": build_metadata,
        "relevantFiles": [
            entry["file"] for entry in controllers
        ] + [entry["file"] for entry in configuration_files] + build_metadata.get("buildFiles", []),
    }


def write_analysis_output(payload: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze source and configuration for documentation")
    parser.add_argument(
        "--output",
        default="docs/generated/source-analysis.json",
        help="Path to write the analysis output JSON (default: docs/generated/source-analysis.json)",
    )
    args = parser.parse_args()

    repo_root = repo_root_from_script()
    output_path = (repo_root / args.output).resolve()
    payload = build_analysis_payload(repo_root)
    payload["generatedAt"] = datetime.now(timezone.utc).isoformat()
    write_analysis_output(payload, output_path)

    print(f"Source analysis completed. Output written to {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
