#!/usr/bin/env python3
"""End-to-end checks of the mdp collection features: inventory, typed connections, tags and freshness.

Runs standalone from the package root: python3 -m unittest discover -s tests
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


PACKAGE = Path(__file__).resolve().parents[1]


class CollectionFeatureTests(unittest.TestCase):
    def test_structured_inventory_tool_builds_checks_and_detects_errors(self) -> None:
        tool = PACKAGE / "scripts" / "markdown_protocol.py"
        with tempfile.TemporaryDirectory() as temporary:
            collection = Path(temporary)
            (collection / "topics").mkdir()
            readme = textwrap.dedent(
                """\
                ---
                role: front-door
                summary: Fixture collection.
                read_when: Start here.
                ---
                # Collection

                [Index](INDEX.md) · [Inventory](INVENTORY.md)

                ---

                [⌂ Home](#collection)
                """
            )
            index = textwrap.dedent(
                """\
                ---
                role: index
                parent: README.md
                summary: Human topic map.
                read_when: Browse the fixture.
                ---
                # Index

                - [Topic](topics/topic.md)

                ---

                [⌂ Home](README.md)
                """
            )
            topic = textwrap.dedent(
                """\
                ---
                role: topic
                parent: ../INDEX.md
                summary: One fixture topic.
                read_when: Test the checker.
                tags:
                  - domain/testing
                  - use/validation
                ---
                # Topic

                ## In brief

                Compact fixture.

                ## Core

                Authoritative fixture content.

                ---

                [⌂ Home](../README.md)
                """
            )
            (collection / "README.md").write_text(readme, encoding="utf-8")
            (collection / "INDEX.md").write_text(index, encoding="utf-8")
            topic_path = collection / "topics" / "topic.md"
            topic_path.write_text(topic, encoding="utf-8")

            before_index = (collection / "INDEX.md").read_text(encoding="utf-8")
            built = subprocess.run(
                [sys.executable, str(tool), "inventory", str(collection), "--write"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, built.returncode, built.stderr)
            self.assertEqual(before_index, (collection / "INDEX.md").read_text(encoding="utf-8"))
            inventory = (collection / "INVENTORY.md").read_text(encoding="utf-8")
            self.assertIn("Generated file. Do not edit directly.", inventory)
            self.assertIn("## Optional", inventory)

            checked = subprocess.run(
                [sys.executable, str(tool), "check", str(collection), "--require-properties"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, checked.returncode, checked.stdout + checked.stderr)
            self.assertIn("PASS", checked.stdout)

            long_core = "\n".join(f"Line {number}." for number in range(31))
            topic_path.write_text(
                topic.replace("Authoritative fixture content.", long_core),
                encoding="utf-8",
            )
            warned = subprocess.run(
                [sys.executable, str(tool), "check", str(collection), "--require-properties"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, warned.returncode, warned.stdout + warned.stderr)
            self.assertIn("WARNING", warned.stdout)
            self.assertIn("review threshold is 30", warned.stdout)

            topic_path.write_text(
                topic.replace("Authoritative fixture content.", "[Broken](missing.md)"),
                encoding="utf-8",
            )
            broken = subprocess.run(
                [sys.executable, str(tool), "check", str(collection), "--require-properties"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(1, broken.returncode)
            self.assertIn("broken link", broken.stdout)

            topic_path.write_text(topic.replace("summary:", "note:"), encoding="utf-8")
            missing = subprocess.run(
                [sys.executable, str(tool), "inventory", str(collection), "--check"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(1, missing.returncode)
            self.assertIn("missing summary", missing.stderr)

    def test_typed_connections_learning_order_and_cycle_detection(self) -> None:
        tool = PACKAGE / "scripts" / "markdown_protocol.py"
        with tempfile.TemporaryDirectory() as temporary:
            collection = Path(temporary)
            readme = """# Collection\n\n- [A](a.md)\n- [B](b.md)\n- [C](c.md)\n\n---\n\n[⌂ Home](#collection)\n"""
            a = """# A\n\n## Connections\n\n- Next: [B](b.md)\n- Deeper: [B](b.md)\n\n---\n\n[⌂ Home](README.md) · [Next →](b.md)\n"""
            b = """# B\n\n## Connections\n\n- Parent: [A](a.md)\n- Prerequisite: [C](c.md)\n\n---\n\n[← Previous](a.md) · [⌂ Home](README.md)\n"""
            c = """# C\n\n## Connections\n\n- Related: [A](a.md)\n\n---\n\n[⌂ Home](README.md)\n"""
            for name, content in (("README.md", readme), ("a.md", a), ("b.md", b), ("c.md", c)):
                (collection / name).write_text(content, encoding="utf-8")

            checked = subprocess.run(
                [sys.executable, str(tool), "check", str(collection)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, checked.returncode, checked.stdout + checked.stderr)

            graphed = subprocess.run(
                [sys.executable, str(tool), "graph", str(collection), "--topic", "b.md"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, graphed.returncode, graphed.stdout + graphed.stderr)
            self.assertIn("Required before b.md:\n- c.md", graphed.stdout)
            self.assertIn("Orphans:\n- None.", graphed.stdout)
            order = graphed.stdout.split("Required before", 1)[0]
            self.assertLess(order.index("c.md"), order.index("b.md"))

            (collection / "a.md").write_text(a.replace("- Deeper: [B](b.md)\n", ""), encoding="utf-8")
            unpaired = subprocess.run(
                [sys.executable, str(tool), "check", str(collection)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(1, unpaired.returncode)
            self.assertIn("not reciprocated by Deeper", unpaired.stdout)
            (collection / "a.md").write_text(a, encoding="utf-8")

            (collection / "c.md").write_text(
                c.replace("- Related: [A](a.md)", "- Prerequisite: [B](b.md)"),
                encoding="utf-8",
            )
            cycled = subprocess.run(
                [sys.executable, str(tool), "check", str(collection)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(1, cycled.returncode)
            self.assertIn("prerequisite cycle", cycled.stdout)

    def test_tag_vocabulary_validation_and_and_filtering(self) -> None:
        tool = PACKAGE / "scripts" / "markdown_protocol.py"
        with tempfile.TemporaryDirectory() as temporary:
            collection = Path(temporary)
            (collection / "README.md").write_text(
                "# Collection\n\n- [A](a.md)\n- [B](b.md)\n\n---\n\n[⌂ Home](#collection)\n",
                encoding="utf-8",
            )
            a = """---
role: topic
parent: README.md
summary: Control learning topic.
read_when: Learn control.
tags:
  - domain/control
  - use/learning
---
# A

---

[⌂ Home](README.md)
"""
            b = a.replace("Control learning topic.", "Control reference topic.").replace(
                "use/learning", "use/reference"
            ).replace("# A", "# B")
            (collection / "a.md").write_text(a, encoding="utf-8")
            (collection / "b.md").write_text(b, encoding="utf-8")

            checked = subprocess.run(
                [sys.executable, str(tool), "check", str(collection)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, checked.returncode, checked.stdout + checked.stderr)

            vocabulary = subprocess.run(
                [sys.executable, str(tool), "tags", str(collection)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, vocabulary.returncode)
            self.assertIn("domain/control: 2 file(s)", vocabulary.stdout)

            filtered = subprocess.run(
                [
                    sys.executable,
                    str(tool),
                    "tags",
                    str(collection),
                    "--tag",
                    "domain/control",
                    "--tag",
                    "use/learning",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, filtered.returncode)
            self.assertIn("a.md", filtered.stdout)
            self.assertNotIn("b.md", filtered.stdout)

            (collection / "a.md").write_text(
                a.replace("use/learning", "audience/learner"), encoding="utf-8"
            )
            invalid = subprocess.run(
                [sys.executable, str(tool), "check", str(collection)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(1, invalid.returncode)
            self.assertIn("invalid tag", invalid.stdout)

    def test_optional_freshness_properties_and_review_cutoff(self) -> None:
        tool = PACKAGE / "scripts" / "markdown_protocol.py"
        with tempfile.TemporaryDirectory() as temporary:
            collection = Path(temporary)
            (collection / "README.md").write_text(
                "# Collection\n\n- [Topic](topic.md)\n\n---\n\n[⌂ Home](#collection)\n",
                encoding="utf-8",
            )
            topic = """---
role: topic
parent: README.md
summary: Reviewed topic.
read_when: Freshness matters.
status: active
reviewed: 2025-06-01
---
# Topic

---

[⌂ Home](README.md)
"""
            path = collection / "topic.md"
            path.write_text(topic, encoding="utf-8")

            stale = subprocess.run(
                [
                    sys.executable,
                    str(tool),
                    "check",
                    str(collection),
                    "--reviewed-since",
                    "2026-01-01",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, stale.returncode, stale.stdout + stale.stderr)
            self.assertIn("WARNING", stale.stdout)
            self.assertIn("last reviewed 2025-06-01", stale.stdout)

            current = subprocess.run(
                [
                    sys.executable,
                    str(tool),
                    "check",
                    str(collection),
                    "--reviewed-since",
                    "2025-01-01",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, current.returncode, current.stdout + current.stderr)
            self.assertNotIn("not reviewed since", current.stdout)

            path.write_text(topic.replace("status: active", "status: uncertain"), encoding="utf-8")
            invalid = subprocess.run(
                [sys.executable, str(tool), "check", str(collection)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(1, invalid.returncode)
            self.assertIn("invalid status", invalid.stdout)


if __name__ == "__main__":
    unittest.main()
