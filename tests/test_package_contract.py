from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


PACKAGE = Path(__file__).resolve().parents[1]


class PackageContractTests(unittest.TestCase):
    """Package-owned instruction, navigation, and editor-profile contracts."""

    def read(self, relative: str) -> str:
        return (PACKAGE / relative).read_text(encoding="utf-8")

    def test_native_activation_and_named_commands_are_documented(self) -> None:
        metadata = self.read("agents/openai.yaml")
        entry = self.read("SKILL.md")
        commands = self.read("references/named-commands.md")
        compact_commands = " ".join(commands.split())

        self.assertIn("allow_implicit_invocation: true", metadata)
        self.assertIn("including Markdown changed inside another task", entry)
        self.assertIn("Reading Markdown as input alone is not activation", " ".join(entry.split()))
        self.assertIn("typed `Deeper` relative link", commands)
        self.assertIn("typed\n   `Parent` relative link", commands)
        self.assertIn("read-only structural check", compact_commands)
        self.assertIn("do not bypass the review gate", compact_commands)

    def test_writes_use_the_proportional_review_gate(self) -> None:
        entry = self.read("SKILL.md")
        workflow = self.read("references/review-workflow.md")

        self.assertIn("[review-workflow.md]", entry)
        self.assertIn("Before writing", entry)
        self.assertIn("wait for agreement", entry)
        self.assertIn("Local edit", workflow)
        self.assertIn("Collection change", workflow)
        self.assertIn("Implement only the agreed design", workflow)
        self.assertIn("user's direct edit is new source state", workflow)

    def test_compact_local_edit_loading_path_stays_within_budget(self) -> None:
        parts = [self.read("SKILL.md")]
        for relative in (
            "references/review-workflow.md",
            "references/validation.md",
        ):
            parts.append(self.read(relative).split("\n## Details", 1)[0])
        compact = "".join(parts)

        self.assertLessEqual(len(compact.encode("utf-8")), 6_000)
        self.assertLessEqual(len(compact.splitlines()), 100)

        entry = self.read("SKILL.md")
        self.assertNotIn("Every task: [core]", entry)
        self.assertIn("Creating or reorganizing a collection, ownership, or navigation", entry)

    def test_details_sections_do_not_introduce_authority(self) -> None:
        core = self.read("references/core-protocol.md")
        layouts = self.read("references/layouts.md")
        validation = self.read("references/validation.md")

        self.assertIn("Everything a reader must obey or rely on appears above", core)
        self.assertIn("they never add,\n   weaken, or replace a rule", core)
        self.assertIn("No new rule begins here", layouts)
        self.assertIn("appear above\n  the first `## Details`", validation)

    def test_compactness_and_visual_guidance_remain_proportional(self) -> None:
        layouts = self.read("references/layouts.md")
        workflow = self.read("references/review-workflow.md")
        compact_layouts = " ".join(layouts.split())

        self.assertIn("roughly 30 non-empty", layouts)
        self.assertIn("roughly 60", layouts)
        self.assertIn("warnings, not failures", layouts)
        self.assertIn("A diagram is not mandatory", layouts)
        self.assertIn("nontrivial Compact profile", compact_layouts)
        self.assertIn("Patterns used", workflow)
        self.assertIn("omit the line for ordinary headings", " ".join(workflow.split()).lower())

    def test_addon_contract_keeps_extensions_optional_and_bounded(self) -> None:
        entry = self.read("SKILL.md")
        routes = self.read("references/addons/routes.md")
        contract = self.read("references/addons/add-on-contract.md")

        self.assertIn("[add-on routes](references/addons/routes.md)", entry)
        self.assertIn("[add-on-contract.md](add-on-contract.md)", routes)
        for field in (
            "Trigger",
            "Blocks",
            "Layout variants",
            "Generated views",
            "Checks",
            "Composition",
            "Boundaries",
        ):
            self.assertIn(field, contract)
        compact = " ".join(contract.split())
        self.assertIn("may not weaken the core invariants", compact)
        self.assertIn("minimum useful combination", compact)
        self.assertIn("Selection grants no network", compact)

        for name in (
            "education.md",
            "codebase.md",
            "research-notes.md",
            "decision-records.md",
            "runbooks.md",
            "visual-extras.md",
            "slides.md",
            "skill-package.md",
        ):
            with self.subTest(name=name):
                addon = self.read(f"references/addons/{name}")
                self.assertIn("## Add-on declaration", addon)
                self.assertIn("| Trigger |", addon)
                self.assertIn("| Generated views |", addon)
                self.assertIn("| Boundaries |", addon)

    def test_education_addon_is_selective_restrained_and_source_aware(self) -> None:
        routes = self.read("references/addons/routes.md")
        education = self.read("references/addons/education.md")
        compact = " ".join(education.split())

        self.assertIn("[education.md](education.md)", routes)
        self.assertIn("the user does not have to choose", education)
        self.assertIn("Choose the minimum useful combination", education)
        self.assertIn("not a required file layout", education)
        self.assertNotIn("Add every", education)
        self.assertIn("Use headings and whitespace before decorative devices", education)
        self.assertIn("Avoid decorative icons", education)
        self.assertIn("Write short, compact, straightforward sentences", education)
        self.assertIn("preserve the reader's established tone", education)
        self.assertIn("later manual edits", education)
        for field in ("title", "authorship", "year", "source type", "link target", "relevance"):
            self.assertIn(field, education)
        self.assertIn("Prefer a DOI, publisher page, arXiv record", education)
        self.assertIn("Do not invent a citation", education)
        self.assertIn("grants no network or acquisition authority", compact)

    def test_education_addon_keeps_recall_and_glossary_paths_optional(self) -> None:
        education = self.read("references/addons/education.md")
        compact = " ".join(education.split())

        self.assertIn("## Optional recall card", education)
        self.assertIn("**Question:**", education)
        self.assertIn("<details>", education)
        self.assertIn("Prefer the\nQuick Review / Fact Card", education)
        self.assertIn("## Glossary block", education)
        self.assertIn("typed `Prerequisite` connections", education)
        self.assertIn("## Optional generated review deck", education)
        self.assertIn("links every card back to its owning topic", education)
        self.assertIn("does not itself authorize or provide a generator", compact)
        self.assertIn("hide no prerequisite", education)

    def test_codebase_addon_is_bounded_portable_and_verifiable(self) -> None:
        routes = self.read("references/addons/routes.md")
        codebase = self.read("references/addons/codebase.md")
        compact = " ".join(codebase.split())

        self.assertIn("[codebase.md](codebase.md)", routes)
        self.assertIn("select the smallest useful combination of views", compact)
        self.assertIn("Do not require every zoom level", codebase)
        for scale in ("Small", "Medium", "Complex"):
            self.assertIn(scale, codebase)
        for view in ("Numbered workflow journey", "File responsibility map", "Change-impact guide"):
            self.assertIn(view, codebase)
        self.assertIn("file or symbol", codebase)
        self.assertIn("verified by", codebase)
        self.assertIn("same names and numbers across diagrams and text", codebase)
        self.assertIn("portable baseline", compact)
        self.assertIn("Preserve a text fallback", codebase)
        self.assertIn("Do not hand-maintain a complete import graph", codebase)
        self.assertIn("Graphviz", codebase)
        self.assertIn("No mandatory tool", codebase)
        self.assertIn("## Optional generated Python import map", codebase)
        self.assertIn("standard library `ast` module", compact)
        self.assertIn("never present the result as a complete runtime call graph", compact)
        self.assertIn("one small package diagram", compact)
        self.assertIn("sortable text table", compact)
        self.assertIn("## Entry points and where-used views", codebase)
        self.assertIn("bounded reverse lookup", codebase)
        self.assertIn("Source code and tests decide behavior", compact)

    def test_specialized_addons_preserve_their_own_boundaries(self) -> None:
        routes = self.read("references/addons/routes.md")

        research = self.read("references/addons/research-notes.md")
        research_compact = " ".join(research.split())
        self.assertIn("[research-notes.md](research-notes.md)", routes)
        self.assertIn("Research Notes Add-on", self.read("INDEX.md"))
        self.assertIn("citation_key", research)
        for status in ("exact", "empirical", "numerical", "proposed", "uncertain"):
            self.assertIn(f"| {status} |", research)
        self.assertIn("`research-context-scout`", research)
        self.assertIn("does not establish influence, priority, or consensus", research_compact)
        self.assertIn("No citation, quotation, result, or access status is invented", research)

        decisions = self.read("references/addons/decision-records.md")
        decisions_compact = " ".join(decisions.split())
        self.assertIn("[decision-records.md](decision-records.md)", routes)
        for heading in ("Context", "Decision", "Consequences", "Alternatives considered"):
            self.assertIn(f"## {heading}", decisions)
        self.assertIn("proposed | accepted | deprecated | superseded", decisions)
        self.assertIn("link both directions", decisions_compact)
        self.assertIn("copying a meeting transcript", decisions)

        runbooks = self.read("references/addons/runbooks.md")
        runbooks_compact = " ".join(runbooks.split())
        self.assertIn("[runbooks.md](runbooks.md)", routes)
        self.assertIn("\\text{Action} + \\text{Expected result} + \\text{Verification}", runbooks)
        for label in ("**Action:**", "**Expected:**", "**Verify:**", "**Stop if:**"):
            self.assertIn(label, runbooks)
        self.assertIn("## Rollback or recovery", runbooks)
        self.assertIn("does not grant permission to execute itself", runbooks_compact)
        self.assertIn("Sample output is visibly illustrative", runbooks)

    def test_visual_and_slide_addons_keep_source_text_authoritative(self) -> None:
        routes = self.read("references/addons/routes.md")

        visual = self.read("references/addons/visual-extras.md")
        visual_compact = " ".join(visual.split())
        self.assertIn("[visual-extras.md](visual-extras.md)", routes)
        for heading in ("Markmap hierarchy view", "Foam navigation graph", "Editable SVG for large diagrams"):
            self.assertIn(f"## {heading}", visual)
        self.assertIn("portable labelled relative links remain the default", visual_compact)
        self.assertIn("not as semantic or evidentiary authority", visual_compact)
        self.assertIn("do not keep only a PNG export", visual_compact)
        self.assertIn("status is `unverified`", visual)

        slides = self.read("references/addons/slides.md")
        slides_compact = " ".join(slides.split())
        self.assertIn("[slides.md](slides.md)", routes)
        self.assertIn("marp: true", slides)
        self.assertIn("topic note remains the owner", slides_compact)
        self.assertIn("one major idea per slide", slides)
        self.assertIn("preview and each export format as separate targets", slides_compact)
        self.assertIn("does not prove", slides_compact)
        self.assertIn("reported separately as `unverified`", slides_compact)
        self.assertIn("Do not enable unrestricted HTML for an untrusted deck", slides)

    def test_navigation_map_uses_role_and_depth_vocabulary(self) -> None:
        entry = self.read("SKILL.md")
        index = self.read("INDEX.md")
        compact_entry = " ".join(entry.split())

        self.assertIn("[INDEX.md](INDEX.md)", entry)
        self.assertIn("ordinary tasks do not require it", compact_entry)
        for heading in ("Choose a route", "Package map", "Core references", "Add-ons"):
            self.assertIn(f"## {heading}", index)
        self.assertIn("compact operational entry", index)

        paths = (
            "SKILL.md",
            "INDEX.md",
            "references/core-protocol.md",
            "references/layouts.md",
            "references/validation.md",
            "references/pilot-report.md",
            "references/addons/skill-package.md",
        )
        combined = "\n".join(self.read(path) for path in paths).lower()
        for phrase in (
            "compact machine entry",
            "machine entry:",
            "human entry:",
            "human depth",
            "human route map",
            "model routes",
        ):
            self.assertNotIn(phrase, combined)
        self.assertIn("compact operational entry", combined)
        self.assertIn("navigation map", combined)
        self.assertIn("optional depth", combined)

    def test_skill_package_addon_has_adaptive_profiles_and_clear_owners(self) -> None:
        routes = self.read("references/addons/routes.md")
        addon = self.read("references/addons/skill-package.md")

        self.assertIn("[skill-package.md](skill-package.md)", routes)
        for profile in ("Minimal", "Routed", "Navigable", "Tool-bearing"):
            self.assertIn(profile, addon)
        self.assertIn("Target skill", addon)
        self.assertIn("Native skill-creation guidance", addon)
        self.assertIn("Markdown Protocol", addon)
        self.assertIn("Skills Orchestrator", addon)
        self.assertIn("does not authorize a repository-wide migration", addon)

    def test_navigation_footer_is_a_required_portable_structure(self) -> None:
        entry = self.read("SKILL.md")
        core = self.read("references/core-protocol.md")
        layouts = self.read("references/layouts.md")
        validation = self.read("references/validation.md")

        self.assertIn("Every authored page ends with the", entry)
        self.assertIn("Home points to the nearest Front Door", core)
        self.assertIn(
            "[← Previous](previous.md) · [⌂ Home](../README.md) · [Next →](next.md)",
            core,
        )
        self.assertIn("curated sequence", layouts)
        self.assertIn("Home footers", validation)

    def test_every_package_markdown_file_has_a_valid_home_footer(self) -> None:
        footer_link = re.compile(r"\[[^]]+\]\(([^)#]+\.md)(?:#[^)]+)?\)")
        local_anchor = re.compile(r"\[[^]]+\]\(#([^)]+)\)")

        for path in PACKAGE.rglob("*.md"):
            with self.subTest(path=path.relative_to(PACKAGE)):
                text = path.read_text(encoding="utf-8")
                lines = [line for line in text.splitlines() if line.strip()]
                footer = lines[-1]
                self.assertRegex(footer, r"\[⌂ Home\]\([^)]+\)")
                self.assertEqual(1, footer.count("[⌂ Home]"))
                self.assertEqual("---", lines[-2])
                for target in footer_link.findall(footer):
                    self.assertTrue((path.parent / target).resolve().is_file(), target)
                headings = {
                    re.sub(r"[^a-z0-9 -]", "", heading.lower()).strip().replace(" ", "-")
                    for heading in re.findall(r"^#{1,6}\s+(.+)$", text, flags=re.MULTILINE)
                }
                for anchor in local_anchor.findall(footer):
                    self.assertIn(anchor, headings)

    def test_previous_and_next_footer_links_are_reciprocal(self) -> None:
        relation = re.compile(r"\[(← Previous|Next →)\]\(([^)#]+\.md)(?:#[^)]+)?\)")
        inverse = {"← Previous": "Next →", "Next →": "← Previous"}

        for path in PACKAGE.rglob("*.md"):
            footer = [
                line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
            ][-1]
            for label, target in relation.findall(footer):
                target_path = (path.parent / target).resolve()
                target_footer = [
                    line
                    for line in target_path.read_text(encoding="utf-8").splitlines()
                    if line.strip()
                ][-1]
                expected = path.relative_to(target_path.parent).as_posix()
                with self.subTest(path=path.relative_to(PACKAGE), target=target):
                    self.assertIn(f"[{inverse[label]}]({expected})", target_footer)

    def test_entry_index_and_gallery_links_resolve(self) -> None:
        entry = PACKAGE / "SKILL.md"
        for target in re.findall(r"\[[^]]+\]\(([^)]+\.md)\)", entry.read_text(encoding="utf-8")):
            self.assertTrue((entry.parent / target).resolve().is_file(), target)

        index = PACKAGE / "INDEX.md"
        for target in re.findall(
            r"\[[^]]+\]\(([^)#]+\.md)(?:#[^)]+)?\)", index.read_text(encoding="utf-8")
        ):
            self.assertTrue((index.parent / target).resolve().is_file(), target)

        gallery = PACKAGE / "references" / "markdown-patterns.md"
        targets = re.findall(
            r"\[[^]]+\]\((formatting-examples/[^)]+\.md)\)",
            gallery.read_text(encoding="utf-8"),
        )
        self.assertGreaterEqual(len(targets), 15)
        self.assertEqual(len(targets), len(set(targets)))
        for target in targets:
            path = gallery.parent / target
            self.assertTrue(path.is_file(), target)
            self.assertLess(path.stat().st_size, 8_000, target)

    def test_phase_two_gallery_and_renderer_matrix_are_explicit(self) -> None:
        gallery = self.read("references/markdown-patterns.md")
        visual = self.read("references/visual-patterns.md")

        for name in (
            "17-editor-folding.md",
            "18-markmap-view.md",
            "19-editable-svg-diagrams.md",
            "20-renderer-verification-fixture.md",
        ):
            self.assertIn(name, gallery)
            self.assertTrue((PACKAGE / "references" / "formatting-examples" / name).is_file())
        self.assertIn("### Renderer matrix", gallery)
        self.assertIn("visual pass pending", gallery)
        self.assertIn("MPE 0.8.39", gallery)
        self.assertIn("P = max(N / 12, E / 12, L / 8)", visual)
        self.assertIn("A = width / height", visual)

    def test_portable_vscode_pack_is_small_safe_and_reproducible(self) -> None:
        extensions = json.loads((PACKAGE / ".vscode" / "extensions.json").read_text(encoding="utf-8"))
        self.assertEqual(
            ["shd101wyy.markdown-preview-enhanced", "davidanson.vscode-markdownlint"],
            extensions["recommendations"],
        )
        self.assertIn("nettrash.md-vscode", extensions["unwantedRecommendations"])

        settings = json.loads((PACKAGE / ".vscode" / "settings.json").read_text(encoding="utf-8"))
        self.assertTrue(settings["markdown.validate.enabled"])
        self.assertEqual("prompt", settings["markdown.updateLinksOnFileMove.enabled"])
        self.assertTrue(settings["markdown-preview-enhanced.scrollSync"])
        self.assertFalse(settings["markdown-preview-enhanced.enableWikiLinkSyntax"])
        self.assertFalse(settings["markdown-preview-enhanced.enableScriptExecution"])
        self.assertFalse(settings["markdown-preview-enhanced.enablePreviewScripts"])

        lint = json.loads((PACKAGE / ".markdownlint.jsonc").read_text(encoding="utf-8"))
        self.assertFalse(lint["default"])
        self.assertEqual(["details", "summary"], lint["MD033"]["allowed_elements"])
        self.assertNotIn("MD013", lint)

        bindings = json.loads(
            (PACKAGE / "assets" / "vscode" / "keybindings.json").read_text(encoding="utf-8")
        )
        self.assertTrue(any(item.get("mac") == "cmd+alt+v" for item in bindings))
        commands = {item["command"] for item in bindings}
        self.assertIn("markdown-preview-enhanced.openPreviewToTheSide", commands)
        self.assertIn("latex-workshop.view", commands)

    def test_vscode_setup_and_pilot_record_known_boundaries(self) -> None:
        guide = self.read("references/vscode-setup.md")
        self.assertIn("back up User `keybindings.json`", guide)
        self.assertIn("recommendations do not", guide)
        self.assertIn("Command-Option-V", guide)
        self.assertIn("true rendering also executes R code", guide)

        pilot = self.read("references/pilot-report.md")
        self.assertIn("its own first real pilot", pilot)
        self.assertIn("without maintaining parallel audience-specific copies", pilot)
        self.assertIn("Snippets are intentionally deferred", pilot)
        self.assertIn("pending macOS Computer Use permission", pilot)

    def test_renderer_fixture_and_math_guidance_cover_known_risks(self) -> None:
        fixture = self.read("references/formatting-examples/20-renderer-verification-fixture.md")
        self.assertGreaterEqual(fixture.count("```mermaid"), 3)
        self.assertIn("$E = mc^2$", fixture)
        self.assertIn("\\begin{aligned}", fixture)
        self.assertIn("<details>", fixture)
        self.assertIn("> [!WARNING]", fixture)
        self.assertIn("Text fallback", fixture)

        math_example = self.read("references/formatting-examples/13-mathematical-expressions.md")
        self.assertIn("## Provisional house style", math_example)
        self.assertIn("VS Code uses KaTeX", math_example)
        self.assertIn("GitHub uses MathJax", math_example)
        self.assertIn("Do not depend on `\\label`, `\\ref`", math_example)

    def test_core_documents_use_portable_links(self) -> None:
        for name in (
            "core-protocol.md",
            "layouts.md",
            "markdown-patterns.md",
            "review-workflow.md",
            "visual-patterns.md",
            "validation.md",
        ):
            with self.subTest(name=name):
                self.assertNotIn("[[", self.read(f"references/{name}"))

    def test_layers_are_defined_by_depth_never_by_audience(self) -> None:
        def head(relative: str) -> str:
            return " ".join(self.read(relative).split("\n## Details", 1)[0].split())

        entry = " ".join(self.read("SKILL.md").split())
        core = head("references/core-protocol.md")

        self.assertIn("Layer by depth, never by audience", entry)
        self.assertIn("never in a parallel audience copy", entry)
        self.assertIn("report such a split, or a rule forcing one, in the proposal", entry)
        self.assertIn("never by who reads them", core)
        self.assertIn("A split by audience always obstructs them", core)
        self.assertIn("keep or restore that layering", core)
        self.assertIn("name the conflict in the proposal, offer the conversion", core)
        self.assertIn(
            "including any split by audience or rule that forces one",
            head("references/review-workflow.md"),
        )
        self.assertIn("extend no parallel audience copy", head("references/validation.md"))
        self.assertIn(
            "### Converting a collection split by audience", self.read("references/layouts.md")
        )

    def test_audience_labels_appear_only_where_they_are_forbidden(self) -> None:
        label = re.compile(r"\b(?:human|machine|model|agent)-facing\b")
        allowed = {"SKILL.md", "references/core-protocol.md"}
        for path in PACKAGE.rglob("*.md"):
            relative = path.relative_to(PACKAGE).as_posix()
            if any(part.startswith(".") for part in path.relative_to(PACKAGE).parts):
                continue
            for paragraph in re.split(r"\n\s*\n", path.read_text(encoding="utf-8")):
                if not label.search(paragraph):
                    continue
                with self.subTest(path=relative):
                    self.assertIn(relative, allowed)
                    self.assertRegex(paragraph.lower(), r"never|nothing is labelled")


if __name__ == "__main__":
    unittest.main()
