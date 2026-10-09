# Changelog

Versions follow SemVer, and `pyproject.toml` owns the version. Below 1.0.0 a MINOR
release may break, and its entry says so. Earlier history is in the Git log.

## 0.2.0

Not yet tagged. Hardened verification and release flow: `mdp verify --html-links`,
`mdp doctor` source and workspace checksums, an explicit `mdp update check`, a
complete-package verification script (`scripts/verify_package.py`) with CI on
Python 3.10 and 3.13, and package contract tests. Collection feature tests
(inventory, typed connections, tags and freshness) now live here as well.

## 0.1.1

Layers are named by depth and role instead of audience, and the generated
inventory round-trips cleanly.

---

[⌂ Home](README.md)
