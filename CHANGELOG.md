# Changelog

Versions follow SemVer, and `pyproject.toml` owns the version. Below 1.0.0 a MINOR
release may break, and its entry says so. Earlier history is in the Git log.

## 0.3.0

Layers are defined by depth and role, never by audience: no layer, file or
heading is labelled for a kind of reader. When updating an existing collection,
new content goes to its single owner at the right depth; a split by audience,
or a project rule that forces a parallel copy, is reported in the proposal with
an offer to convert it instead of being extended. Adds a conversion procedure
to the layouts reference and tests for both rules. Behavior change: writes into
an existing audience-split collection now pause for that decision.

## 0.2.0

Hardened verification and release flow: `mdp verify --html-links`,
`mdp doctor` source and workspace checksums, an explicit `mdp update check`, a
complete-package verification script (`scripts/verify_package.py`) with CI on
Python 3.10 and 3.13, and package contract tests. Collection feature tests
(inventory, typed connections, tags and freshness) now live here as well.

## 0.1.1

Layers are named by depth and role instead of audience, and the generated
inventory round-trips cleanly.

---

[⌂ Home](README.md)
