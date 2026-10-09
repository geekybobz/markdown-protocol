---
role: front-door
summary: Portable entry point for Markdown Protocol users and contributors.
read_when: Start here when installing, sharing, or browsing the package.
---

# Markdown Protocol

Markdown Protocol keeps one linked documentation structure compact at its
edge and explanatory at depth. It includes a Codex skill, linked learning
references, a deterministic `mdp` command, and a reproducible macOS VS Code
pack.

## Start here

- Apply the protocol: [compact operational entry](SKILL.md)
- Browse or maintain the package: [topic index](INDEX.md)
- New collection: `mdp init my-notes --title "My notes"`
- Existing collection: `mdp status .`, then `mdp adopt .`
- Collection verification: `mdp verify .`
- Complete package verification: `python3 scripts/verify_package.py`

Install from a clone with `python3 -m pip install .`, or use an isolated tool
manager with `uv tool install .`. The package has no runtime dependencies
outside the Python standard library. Run `mdp doctor .` after installation.
Updates are never checked in the background: run `mdp update check` explicitly.
Update a clone with `git pull --ff-only` after reading [the changelog](CHANGELOG.md), and
roll back with `git revert` or a checkout of an earlier tag. Skills AI integration is
optional; this repository needs nothing from it.

## Releases

`pyproject.toml` owns the public version and the CLI version must match it. A
release is cut only from a clean package `main` after CI passes: commit and push
the package first, create and push an annotated `v<version>` tag, then publish
the matching GitHub Release. A parent repository may update its package pointer
only after that package commit is available remotely. GitHub's release-only
Watch setting becomes useful after the first release is published.

## Editor setup

Import [`markdown-protocol-macos.code-profile`](assets/vscode/markdown-protocol-macos.code-profile)
through **Profiles: Import Profile**, or follow the auditable manual path in
[VS Code Setup](references/vscode-setup.md). Both preserve the agreed
`Command-Option-V` side-by-side preview behavior.

## Boundaries

The checker validates structure, navigation, and declared protocol metadata.
It does not prove factual correctness or silently rewrite a collection. `fix`
is a dry run unless `--apply` is supplied. Local HTML anchor targets are checked
only when `mdp verify --html-links` is requested.

---

[⌂ Home](README.md) · [Topic index](INDEX.md)
