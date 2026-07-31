# Documentation Workflow Maintainer Guide

## Overview
This repository includes a lightweight documentation generation workflow for the Spring PetClinic application. The workflow produces internal Markdown documentation under the docs folder from repository analysis data and generated content artifacts.

## Running locally
1. Ensure Python 3 is available in the terminal.
2. From the repository root, run:
   - `py -3 scripts/render_markdown.py --trigger-source manual`
3. The workflow will:
   - read the content-mapping artifact under docs/generated,
   - validate and sanitize the generated Markdown,
   - stage the output under docs/.staging,
   - publish the canonical file to docs/generated-documentation.md.

## Running in CI
The workflow is designed to run in GitHub Actions or an equivalent CI environment. A typical CI run should:
1. check out the repository,
2. execute the renderer entry point,
3. inspect the generated Markdown output and run summary artifact.

Example invocation:
- `py -3 scripts/render_markdown.py --trigger-source ci`

## Expected output structure
The generated documentation artifacts are expected under the docs folder:
- docs/generated-documentation.md — canonical published documentation output
- docs/.staging/generated-documentation.md — temporary staged output before publication
- docs/run-summary.json — structured run result and metadata
- docs/generated/source-analysis.json — analysis artifact from the source inspection step
- docs/generated/content-mapping.json — mapped section content used to build the Markdown output

## Troubleshooting
- If the workflow exits with a validation error, inspect the generated content for missing sections or sensitive values that were not redacted.
- If the run summary shows a failed status, review the error message printed by the renderer and fix the underlying generation issue before re-running.
- If the canonical documentation file is missing, confirm that the publish step completed successfully and that the docs folder is writable.
- If the renderer cannot find the mapping artifact, confirm that the analysis and mapping steps completed successfully and that the docs/generated folder contains the expected files.

## Operational expectations
- Treat the generated Markdown as a derived artifact. Update the source files and rerun the workflow when documentation should change.
- Keep the docs folder under version control so the canonical documentation remains reviewable in pull requests.
- Preserve the existing modular structure when extending the workflow. Prefer small, focused updates to the analysis, mapping, validation, publishing, and logging steps.
- Keep generated content free of secrets and ensure any new templates or mappings still satisfy the validation rules.
