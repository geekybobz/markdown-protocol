#!/usr/bin/env python3
"""Run the complete local verification set for the Markdown Protocol package."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKS = (
    ("package tests", (sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests")),
    (
        "Markdown verification",
        (sys.executable, "-B", "scripts/markdown_protocol.py", "verify", ".", "--html-links"),
    ),
    (
        "VS Code profile",
        (sys.executable, "-B", "scripts/build_vscode_profile.py", "--check"),
    ),
)


def main() -> int:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    for label, command in CHECKS:
        print(f"==> {label}", flush=True)
        result = subprocess.run(command, cwd=ROOT, env=environment, check=False)
        if result.returncode:
            print(f"FAIL: {label} exited with {result.returncode}", file=sys.stderr)
            return result.returncode
    print("PASS: complete Markdown Protocol package verification")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
