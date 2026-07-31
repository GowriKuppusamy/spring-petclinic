import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import analyze_source
import map_content
import render_markdown
import validate_markdown


class DocumentationPipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory(dir=REPO_ROOT, prefix="doc-test-", ignore_cleanup_errors=True)
        self.addCleanup(self.temp_dir.cleanup)
        self.temp_path = Path(self.temp_dir.name)

    def _write_sample_repo(self) -> Path:
        repo_root = self.temp_path / "sample-repo"
        repo_root.mkdir(parents=True)
        java_dir = repo_root / "src" / "main" / "java" / "org" / "example"
        java_dir.mkdir(parents=True)
        controller_path = java_dir / "OwnerController.java"
        controller_path.write_text(
            """
            package org.example;

            import org.springframework.stereotype.Controller;
            import org.springframework.web.bind.annotation.GetMapping;
            import org.springframework.web.bind.annotation.RequestMapping;

            @Controller
            @RequestMapping("/owners")
            public class OwnerController {
                @GetMapping("/new")
                public String createOwner() { return "create"; }
            }
            """.strip(),
            encoding="utf-8",
        )
        resources_dir = repo_root / "src" / "main" / "resources"
        resources_dir.mkdir(parents=True)
        (resources_dir / "application.properties").write_text(
            "spring.datasource.url=jdbc:mysql://localhost/test\nspring.datasource.username=petclinic\n",
            encoding="utf-8",
        )
        (repo_root / "pom.xml").write_text(
            "<project><artifactId>petclinic</artifactId><groupId>org.example</groupId><properties><java.version>17</java.version></properties></project>",
            encoding="utf-8",
        )
        return repo_root

    def test_analysis_builds_endpoints_and_configuration(self) -> None:
        repo_root = self._write_sample_repo()

        payload = analyze_source.build_analysis_payload(repo_root)

        self.assertEqual(payload["repository"]["name"], repo_root.name)
        self.assertTrue(payload["controllers"])
        self.assertEqual(payload["controllers"][0]["className"], "OwnerController")
        self.assertEqual(payload["controllers"][0]["endpoints"][0]["path"], "/owners/new")
        self.assertTrue(payload["configurationFiles"])
        self.assertEqual(payload["buildMetadata"]["javaVersion"], "17")

    def test_mapping_payload_contains_required_sections(self) -> None:
        analysis = {
            "controllers": [
                {
                    "className": "OwnerController",
                    "file": "src/main/java/OwnerController.java",
                    "endpoints": [{"method": "GET", "path": "/owners/new"}],
                }
            ],
            "configurationFiles": [{"file": "src/main/resources/application.properties", "properties": [{"key": "spring.datasource.url", "value": "jdbc:mysql://localhost/test"}]}],
            "buildMetadata": {"javaVersion": "17", "buildFiles": ["pom.xml"]},
            "generatedAt": "2026-07-31T00:00:00Z",
        }

        payload = map_content.build_mapping_payload(analysis)

        self.assertIn("apiReference", payload)
        self.assertIn("setupInstructions", payload)
        self.assertIn("configurationDetails", payload)
        self.assertIn("changelog", payload)
        self.assertIn("## API Reference", payload["apiReference"])
        self.assertIn("## Setup and Installation", payload["setupInstructions"])
        self.assertIn("## Environment Configuration", payload["configurationDetails"])
        self.assertIn("## Change History", payload["changelog"])

    def test_validation_redacts_sensitive_values_and_flags_missing_sections(self) -> None:
        markdown = "# Doc\n\n## API Reference\n\n- value\n\n## Setup and Installation\n\n- step\n\n## Environment Configuration\n\n- config\n"

        sanitized, redacted_items = validate_markdown.sanitize_markdown_content(
            markdown + "\npassword=test-secret\napi_key=abc123\njdbc:mysql://localhost/test"
        )
        errors = validate_markdown.validate_markdown_content(sanitized)

        self.assertTrue(redacted_items)
        self.assertIn("[REDACTED]", sanitized)
        self.assertTrue(any("Missing required section" in error for error in errors))

    def test_render_build_markdown_document_uses_mapping_sections(self) -> None:
        mapping = {
            "apiReference": "## API Reference\n\nEndpoint summary",
            "setupInstructions": "## Setup and Installation\n\nInstall Java",
            "configurationDetails": "## Environment Configuration\n\nConfig summary",
            "changelog": "## Change History\n\nUpdated",
        }

        rendered = render_markdown.build_markdown_document(mapping)

        self.assertIn("# Automated Documentation Sync", rendered)
        self.assertIn("## API Reference", rendered)
        self.assertIn("Install Java", rendered)
        self.assertIn("Updated", rendered)

    def test_end_to_end_generation_writes_output_and_run_summary(self) -> None:
        repo_root = self._write_sample_repo()
        docs_dir = repo_root / "docs"
        docs_dir.mkdir(parents=True)
        mapping_path = docs_dir / "generated" / "content-mapping.json"
        mapping_path.parent.mkdir(parents=True)
        mapping_payload = {
            "apiReference": "## API Reference\n\nEndpoint summary",
            "setupInstructions": "## Setup and Installation\n\nInstall Java",
            "configurationDetails": "## Environment Configuration\n\nConfig summary",
            "changelog": "## Change History\n\nUpdated",
        }
        mapping_path.write_text(json.dumps(mapping_payload), encoding="utf-8")

        with mock.patch.object(render_markdown, "repo_root_from_script", return_value=repo_root):
            with mock.patch.object(sys, "argv", ["render_markdown.py", "--trigger-source", "test"]):
                exit_code = render_markdown.main()

        self.assertEqual(exit_code, 0)
        self.assertTrue((docs_dir / "generated-documentation.md").exists())
        self.assertTrue((docs_dir / "run-summary.json").exists())
        summary = json.loads((docs_dir / "run-summary.json").read_text(encoding="utf-8"))
        self.assertEqual(summary["status"], "success")

    def test_regression_snapshot_matches_expected_rendered_output(self) -> None:
        snapshot_path = REPO_ROOT / "tests" / "snapshots" / "expected_generated_document.md"
        mapping = {
            "apiReference": "## API Reference\n\nEndpoint summary",
            "setupInstructions": "## Setup and Installation\n\nInstall Java",
            "configurationDetails": "## Environment Configuration\n\nConfig summary",
            "changelog": "## Change History\n\nUpdated",
        }

        rendered = render_markdown.build_markdown_document(mapping)

        self.assertEqual(rendered, snapshot_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
