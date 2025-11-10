"""Command line entry point for the AWS EBS Optimizer."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from .models import OptimizationRecommendation, VolumeMetrics
from .optimizer import optimize_many


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments."""

    parser = argparse.ArgumentParser(
        description="Analyze AWS EBS volume metrics and produce optimization guidance.",
    )
    parser.add_argument(
        "metrics_file",
        type=Path,
        help="Path to a JSON file containing a list of volume metric objects.",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Optional path to write recommendations as JSON. Prints to stdout when omitted.",
    )

    return parser.parse_args(argv)


def deserialize_metrics(items: Sequence[Mapping[str, object]]) -> list[VolumeMetrics]:
    """Convert an iterable of mapping objects into :class:`VolumeMetrics` values."""

    metrics_objects: list[VolumeMetrics] = []
    for item in items:
        metrics_objects.append(
            VolumeMetrics(
                volume_id=str(item["volume_id"]),
                tier=str(item["tier"]),
                size_gib=int(item["size_gib"]),
                provisioned_iops=int(item.get("provisioned_iops", 0)),
                average_iops=float(item.get("average_iops", 0.0)),
                average_throughput_mbps=float(item.get("average_throughput_mbps", 0.0)),
                burst_balance_percent=float(item.get("burst_balance_percent", 100.0)),
            )
        )

    return metrics_objects


def load_metrics(path: Path) -> list[VolumeMetrics]:
    """Load volume metrics from a JSON file."""

    with path.open("r", encoding="utf-8") as fp:
        raw_metrics = json.load(fp)

    if not isinstance(raw_metrics, list):
        raise ValueError("Metrics file must contain a JSON list of volume metric objects.")

    return deserialize_metrics(raw_metrics)


def format_recommendations(recommendations: Iterable[OptimizationRecommendation]) -> str:
    """Return a human-readable string for the provided recommendations."""

    lines = []
    for rec in recommendations:
        lines.append(f"Volume: {rec.volume_id}")
        lines.append(f"  Action: {rec.action}")
        lines.append(f"  Summary: {rec.summary}")
        lines.append(f"  Details: {rec.details}")
        lines.append("")
    return "\n".join(lines).strip()


def main(argv: Iterable[str] | None = None) -> int:
    """CLI entry point."""

    args = parse_args(argv)
    metrics = load_metrics(args.metrics_file)
    recommendations = optimize_many(metrics)

    if args.output:
        data = [rec.to_dict() for rec in recommendations]
        args.output.write_text(json.dumps(data, indent=2), encoding="utf-8")
    else:
        print(format_recommendations(recommendations))

    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
