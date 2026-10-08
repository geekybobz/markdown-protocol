from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


TOOL = Path(__file__).resolve().parents[1] / "scripts" / "markdown_protocol.py"
PACKAGE = TOOL.parents[1]


class CliTests(unittest.TestCase):
    def run_cli(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(TOOL), *arguments],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_verify_json_has_stable_finding_objects_and_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "README.md").write_text("# Collection\n\n[Missing](gone.md)\n", encoding="utf-8")
            result = self.run_cli("verify", str(root), "--format", "json")
            self.assertEqual(1, result.returncode)
            payload = json.loads(result.stdout)
            self.assertEqual("markdown-protocol.verify.v1", payload["schema"])
            self.assertGreaterEqual(payload["summary"]["errors"], 1)
            finding = payload["findings"][0]
            self.assertEqual({"code", "level", "message", "path"}, set(finding))

    def test_adopt_downgrades_only_footer_and_orphan_findings(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "README.md").write_text("# Collection\n", encoding="utf-8")
            (root / "orphan.md").write_text("# Orphan\n", encoding="utf-8")
            result = self.run_cli("adopt", str(root), "--format", "json")
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(0, payload["summary"]["errors"])
            self.assertGreaterEqual(payload["summary"]["warnings"], 2)

    def test_status_reports_coverage_without_requiring_adoption(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "README.md").write_text(
                "---\nrole: front-door\nsummary: Fixture.\nread_when: Start.\n---\n"
                "# Collection\n\n---\n\n[⌂ Home](#collection)\n",
                encoding="utf-8",
            )
            result = self.run_cli("status", str(root), "--format", "json")
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(1, payload["files"])
            self.assertEqual(1, payload["managed_files"])
            self.assertEqual(1, payload["portable_footers"])
            self.assertEqual("README.md", payload["entry"])

    def test_init_creates_minimal_collection_and_refuses_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "course"
            created = self.run_cli("init", str(root), "--title", "Control Notes")
            self.assertEqual(0, created.returncode, created.stdout + created.stderr)
            self.assertTrue((root / "README.md").is_file())
            self.assertTrue((root / "INDEX.md").is_file())
            verified = self.run_cli("verify", str(root), "--require-properties")
            self.assertEqual(0, verified.returncode, verified.stdout + verified.stderr)
            second = self.run_cli("init", str(root), "--title", "Changed")
            self.assertEqual(1, second.returncode)

    def test_generated_inventory_round_trip_remains_clean(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "course"
            initialized = self.run_cli("init", str(root), "--title", "Control Notes")
            self.assertEqual(0, initialized.returncode, initialized.stdout + initialized.stderr)
            written = self.run_cli("inventory", str(root), "--write")
            self.assertEqual(0, written.returncode, written.stdout + written.stderr)
            checked = self.run_cli("inventory", str(root), "--check")
            self.assertEqual(0, checked.returncode, checked.stdout + checked.stderr)
            verified = self.run_cli("verify", str(root), "--inventory", "INVENTORY.md")
            self.assertEqual(0, verified.returncode, verified.stdout + verified.stderr)
            graph = self.run_cli("graph", str(root), "--format", "text")
            self.assertEqual(0, graph.returncode, graph.stdout + graph.stderr)
            self.assertIn("Orphans:\n- None.", graph.stdout)

    def test_fix_is_dry_run_by_default_and_apply_adds_only_footer(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = "# Collection\n"
            target = root / "README.md"
            target.write_text(source, encoding="utf-8")
            dry = self.run_cli("fix", str(root))
            self.assertEqual(0, dry.returncode, dry.stdout + dry.stderr)
            self.assertEqual(source, target.read_text(encoding="utf-8"))
            self.assertIn("WOULD FIX", dry.stdout)
            applied = self.run_cli("fix", str(root), "--apply")
            self.assertEqual(0, applied.returncode, applied.stdout + applied.stderr)
            self.assertTrue(target.read_text(encoding="utf-8").endswith("[⌂ Home](README.md)\n"))

    def test_graph_supports_json_and_clickable_mermaid(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "README.md").write_text(
                "# Collection\n\n[Topic](topic.md)\n\n---\n\n[⌂ Home](#collection)\n",
                encoding="utf-8",
            )
            (root / "topic.md").write_text(
                "# Topic\n\n---\n\n[⌂ Home](README.md)\n",
                encoding="utf-8",
            )
            mermaid = self.run_cli("graph", str(root), "--format", "mermaid")
            self.assertEqual(0, mermaid.returncode, mermaid.stdout + mermaid.stderr)
            self.assertIn("flowchart TD", mermaid.stdout)
            self.assertIn('click ', mermaid.stdout)
            graph_json = self.run_cli("graph", str(root), "--format", "json")
            payload = json.loads(graph_json.stdout)
            self.assertEqual("markdown-protocol.graph.v1", payload["schema"])
            self.assertEqual(2, len(payload["nodes"]))

    def test_doctor_and_version_are_scriptable(self) -> None:
        version = self.run_cli("version")
        self.assertEqual(0, version.returncode)
        self.assertRegex(version.stdout, r"^mdp \d+\.\d+\.\d+")
        metadata = (PACKAGE / "pyproject.toml").read_text(encoding="utf-8")
        project_version = re.search(r'^version\s*=\s*"([^"]+)"$', metadata, re.MULTILINE)
        self.assertIsNotNone(project_version)
        self.assertEqual(f"mdp {project_version.group(1)}\n", version.stdout)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "README.md").write_text("# Collection\n", encoding="utf-8")
            doctor = self.run_cli("doctor", str(root), "--format", "json")
            self.assertEqual(0, doctor.returncode)
            payload = json.loads(doctor.stdout)
            self.assertEqual("markdown-protocol.doctor.v1", payload["schema"])
            self.assertTrue(payload["python_ok"])
            self.assertIsNone(payload["workspace_match"])
            self.assertEqual([], payload["warnings"])

    def test_doctor_reports_matching_and_stale_workspace_sources(self) -> None:
        current = self.run_cli("doctor", str(PACKAGE), "--format", "json")
        self.assertEqual(0, current.returncode, current.stdout + current.stderr)
        current_payload = json.loads(current.stdout)
        self.assertTrue(current_payload["workspace_match"])
        self.assertEqual([], current_payload["warnings"])

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "scripts").mkdir()
            (root / "README.md").write_text("# Collection\n", encoding="utf-8")
            (root / "pyproject.toml").write_text(
                '[project]\nname = "markdown-protocol"\nversion = "0.2.0"\n',
                encoding="utf-8",
            )
            (root / "scripts" / "markdown_protocol.py").write_text(
                "# stale workspace source\n", encoding="utf-8"
            )
            stale = self.run_cli("doctor", str(root), "--format", "json")
            self.assertEqual(0, stale.returncode, stale.stdout + stale.stderr)
            stale_payload = json.loads(stale.stdout)
            self.assertFalse(stale_payload["workspace_match"])
            self.assertTrue(stale_payload["warnings"])
            self.assertIn("differs from the workspace", stale_payload["warnings"][0])

    def test_verify_html_links_flag_is_machine_readable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "README.md").write_text(
                '# Collection\n\n<a href="gone.md">Missing</a>\n\n---\n\n[⌂ Home](#collection)\n',
                encoding="utf-8",
            )
            result = self.run_cli("verify", str(root), "--html-links", "--format", "json")
            self.assertEqual(1, result.returncode)
            payload = json.loads(result.stdout)
            self.assertTrue(any(item["code"] == "MDP401" for item in payload["findings"]))

    def test_macos_vscode_profile_is_current_and_contains_reference_setup(self) -> None:
        builder = PACKAGE / "scripts" / "build_vscode_profile.py"
        checked = subprocess.run(
            [sys.executable, str(builder), "--check"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, checked.returncode, checked.stdout + checked.stderr)
        profile = json.loads(
            (PACKAGE / "assets" / "vscode" / "markdown-protocol-macos.code-profile").read_text(
                encoding="utf-8"
            )
        )
        settings = json.loads(profile["settings"])
        keybindings = json.loads(profile["keybindings"])
        extensions = json.loads(profile["extensions"])
        self.assertTrue(settings["markdown-preview-enhanced.scrollSync"])
        self.assertEqual("tab", settings["latex-workshop.view.pdf.viewer"])
        commands = {binding["command"] for binding in keybindings}
        self.assertIn("markdown-preview-enhanced.openPreviewToTheSide", commands)
        self.assertIn("latex-workshop.view", commands)
        extension_ids = {item["identifier"]["id"] for item in extensions}
        self.assertEqual(
            {
                "davidanson.vscode-markdownlint",
                "james-yu.latex-workshop",
                "shd101wyy.markdown-preview-enhanced",
            },
            extension_ids,
        )

    def test_update_check_is_explicit_and_machine_readable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            metadata = Path(temporary) / "pyproject.toml"
            metadata.write_text('[project]\nversion = "9.9.9"\n', encoding="utf-8")
            result = self.run_cli(
                "update", "check", "--url", metadata.as_uri(), "--format", "json"
            )
            self.assertEqual(1, result.returncode)
            payload = json.loads(result.stdout)
            self.assertEqual("markdown-protocol.update.v1", payload["schema"])
            self.assertTrue(payload["update_available"])
            self.assertEqual("9.9.9", payload["available"])


if __name__ == "__main__":
    unittest.main()
