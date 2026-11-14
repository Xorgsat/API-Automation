#!/usr/bin/env python3
"""Run full regression test suite with optional parallel execution support."""

import argparse
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="Run full regression test suite.")
    parser.add_argument(
        "-p", "--parallel", action="store_true", help="Execute tests in parallel using pytest-xdist"
    )
    parser.add_argument(
        "-n", "--workers", type=str, default="auto", help="Number of worker processes for xdist (default: auto)"
    )
    args = parser.parse_args()

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-v",
        "--html=reports/regression-report.html",
        "--self-contained-html",
        "--junitxml=reports/junit.xml",
    ]

    if args.parallel:
        cmd.extend(["-n", args.workers])

    print(f"Executing Regression Suite: {' '.join(cmd)}")
    return subprocess.call(cmd)


if __name__ == "__main__":
    sys.exit(main())
