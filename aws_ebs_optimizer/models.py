"""Data models used by the AWS EBS Optimizer."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Tier = Literal["gp2", "gp3", "io1", "io2", "st1", "sc1"]


@dataclass(slots=True)
class VolumeMetrics:
    """Represents utilization metrics for a single EBS volume."""

    volume_id: str
    tier: Tier
    size_gib: int
    provisioned_iops: int
    average_iops: float
    average_throughput_mbps: float
    burst_balance_percent: float

    def validate(self) -> None:
        """Validate basic constraints for the metrics object."""

        if not self.volume_id:
            raise ValueError("volume_id must be provided")
        if self.size_gib <= 0:
            raise ValueError("size_gib must be a positive integer")
        if self.provisioned_iops < 0:
            raise ValueError("provisioned_iops cannot be negative")
        if not (0 <= self.burst_balance_percent <= 100):
            raise ValueError("burst_balance_percent must be between 0 and 100")


@dataclass(slots=True)
class OptimizationRecommendation:
    """Represents an optimization recommendation for an EBS volume."""

    volume_id: str
    action: Literal["maintain", "rightsizing", "upgrade", "investigate"]
    summary: str
    details: str

    def to_dict(self) -> dict[str, str]:
        """Return the recommendation as a dictionary for serialization."""

        return {
            "volume_id": self.volume_id,
            "action": self.action,
            "summary": self.summary,
            "details": self.details,
        }
