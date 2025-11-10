"""Core optimization logic for AWS EBS volumes."""

from __future__ import annotations

from typing import Iterable, List

from .models import OptimizationRecommendation, VolumeMetrics


def optimize_volume(metrics: VolumeMetrics) -> OptimizationRecommendation:
    """Generate a recommendation for a single volume.

    The heuristics implemented here are intentionally simple so the
    application can run without AWS credentials. They mimic typical guidance
    from AWS Trusted Advisor and Compute Optimizer by evaluating volume
    utilization metrics.
    """

    metrics.validate()

    utilization_ratio = metrics.average_iops / metrics.provisioned_iops if metrics.provisioned_iops else 0
    throughput_ratio = metrics.average_throughput_mbps / max(metrics.size_gib * 0.125, 1)

    if metrics.tier == "gp2":
        if metrics.provisioned_iops > 0 and utilization_ratio < 0.2:
            return OptimizationRecommendation(
                volume_id=metrics.volume_id,
                action="rightsizing",
                summary="Convert gp2 to gp3 to lower cost and provision consistent performance.",
                details=(
                    "The volume provisions more IOPS than it consistently consumes. "
                    "Migrating to gp3 allows specifying exact IOPS while reducing cost."
                ),
            )
        if metrics.burst_balance_percent < 20:
            return OptimizationRecommendation(
                volume_id=metrics.volume_id,
                action="upgrade",
                summary="Burst balance is low; consider upgrading to gp3 or io1 for steady performance.",
                details=(
                    "gp2 volumes rely on burst credits. A sustained burst balance below 20% "
                    "indicates the workload would benefit from a gp3 or provisioned IOPS tier."
                ),
            )

    if metrics.tier in {"st1", "sc1"} and throughput_ratio < 0.25:
        return OptimizationRecommendation(
            volume_id=metrics.volume_id,
            action="rightsizing",
            summary="Throughput is low for cold HDD volume; consider gp3 to consolidate capacity.",
            details=(
                "Low throughput on throughput-optimized or cold HDD volumes often "
                "indicates they can be migrated to general purpose SSD for efficiency."
            ),
        )

    if metrics.tier in {"io1", "io2"} and utilization_ratio < 0.1:
        return OptimizationRecommendation(
            volume_id=metrics.volume_id,
            action="rightsizing",
            summary="Provisioned IOPS tier underutilized; migrate to gp3 to reduce spend.",
            details=(
                "The workload consumes less than 10% of the available IOPS. "
                "Switching to gp3 generally offers adequate performance at lower cost."
            ),
        )

    if metrics.tier == "gp3" and utilization_ratio > 0.9:
        return OptimizationRecommendation(
            volume_id=metrics.volume_id,
            action="upgrade",
            summary="IOPS utilization is high; evaluate io2 for critical workloads.",
            details=(
                "The gp3 volume is sustaining more than 90% of provisioned IOPS. "
                "Consider io2 for higher durability and performance headroom."
            ),
        )

    if metrics.average_throughput_mbps > metrics.size_gib * 0.25:
        return OptimizationRecommendation(
            volume_id=metrics.volume_id,
            action="investigate",
            summary="Throughput close to theoretical limits; monitor application patterns.",
            details=(
                "Sustained throughput nearing the volume's limit may precede throttling. "
                "Validate EC2 instance limits and consider upgrading if peaks persist."
            ),
        )

    return OptimizationRecommendation(
        volume_id=metrics.volume_id,
        action="maintain",
        summary="No optimization required at this time.",
        details="Metrics are within expected thresholds for the current configuration.",
    )


def optimize_many(metrics_collection: Iterable[VolumeMetrics]) -> List[OptimizationRecommendation]:
    """Run optimization over an iterable of metrics objects."""

    return [optimize_volume(metrics) for metrics in metrics_collection]
