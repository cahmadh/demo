"""Command line entry point for the AWS EBS Optimizer."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable

from .io_utils import format_recommendations, load_metrics
from .optimizer import optimize_many
from .webapp import serve as serve_ui


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments."""

    parser = argparse.ArgumentParser(
        description="Analyze AWS EBS volume metrics and produce optimization guidance.",
    )
    parser.add_argument(
        "metrics_file",
        nargs="?",
        type=Path,
        help=(
            "Path to a JSON file containing a list of volume metric objects. "
            "Required unless --serve is supplied."
        ),
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Optional path to write recommendations as JSON. Prints to stdout when omitted.",
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Launch the browser UI instead of running a CLI analysis.",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host interface to bind when using --serve. [default: %(default)s]",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="TCP port to bind when using --serve. [default: %(default)s]",
    )

    args = parser.parse_args(argv)

    if args.serve:
        return args

    if args.metrics_file is None:
        parser.error("metrics_file is required unless --serve is provided")

    return args


def main(argv: Iterable[str] | None = None) -> int:
    """CLI entry point."""

    args = parse_args(argv)
    if args.serve:
        serve_ui(host=args.host, port=args.port)
        return 0

    metrics_path = args.metrics_file
    assert metrics_path is not None  # For type checkers

    try:
        metrics = load_metrics(metrics_path)
        recommendations = optimize_many(metrics)
    except Exception as exc:  # pylint: disable=broad-except
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.output:
        data = [rec.to_dict() for rec in recommendations]
        args.output.write_text(json.dumps(data, indent=2), encoding="utf-8")
    else:
        print(format_recommendations(recommendations))

    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
