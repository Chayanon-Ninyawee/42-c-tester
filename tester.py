#!/usr/bin/env python3

import argparse
from pathlib import Path

from framework.runner import run_project


def main():
    parser = argparse.ArgumentParser(
        prog="test-42-c",
        description="42 C project tester",
    )

    parser.add_argument(
        "project",
        help="project to test",
    )

    parser.add_argument(
        "tests",
        nargs="*",
        help="specific tests to run",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="show debugging information",
    )

    args = parser.parse_args()

    run_project(
        project_name=args.project,
        project_dir=Path.cwd(),
        selected_tests=args.tests,
        debug=args.debug,
    )


if __name__ == "__main__":
    main()
