#!/usr/bin/env python3
"""Run smoke test suite for rapid health and availability validation."""

import subprocess
import sys


def main() -> int:
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-m",
        "smoke",
        "-v",
        "--html=reports/smoke-report.html",
        "--self-contained-html",
    ]
    print(f"Executing Smoke Suite: {' '.join(cmd)}")
    return subprocess.call(cmd)


if __name__ == "__main__":
    sys.exit(main())
