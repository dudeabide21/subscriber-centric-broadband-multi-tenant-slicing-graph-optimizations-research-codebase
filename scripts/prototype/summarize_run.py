#!/usr/bin/env python3
"""Generate a deterministic Stage 2 prototype acceptance report."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from scb.prototype import load_prototype_run, render_prototype_summary


def build_arg_parser() -> argparse.ArgumentParser:
    """Build the Stage 2.6 report command-line parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run-dir",
        required=True,
        type=Path,
        help="Directory containing aggregate prototype JSON records.",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Markdown report path.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Load one aggregate run and write its deterministic Markdown report."""

    args = build_arg_parser().parse_args(argv)

    try:
        run = load_prototype_run(args.run_dir)
        report = render_prototype_summary(run)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            report,
            encoding="utf-8",
            newline="\n",
        )
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
