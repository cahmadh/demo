from aws_ebs_optimizer.models import OptimizationRecommendation, VolumeMetrics
from aws_ebs_optimizer.optimizer import optimize_many, optimize_volume


def test_gp2_rightsizing_recommendation():
    metrics = VolumeMetrics(
        volume_id="vol-001",
        tier="gp2",
        size_gib=500,
        provisioned_iops=3000,
        average_iops=200,
        average_throughput_mbps=50,
        burst_balance_percent=90,
    )

    recommendation = optimize_volume(metrics)
    assert recommendation.action == "rightsizing"
    assert "gp3" in recommendation.summary


def test_gp3_upgrade_recommendation():
    metrics = VolumeMetrics(
        volume_id="vol-002",
        tier="gp3",
        size_gib=100,
        provisioned_iops=4000,
        average_iops=3800,
        average_throughput_mbps=25,
        burst_balance_percent=100,
    )

    recommendation = optimize_volume(metrics)
    assert recommendation.action == "upgrade"


def test_optimize_many_returns_all_results():
    metrics_list = [
        VolumeMetrics(
            volume_id="vol-003",
            tier="io1",
            size_gib=200,
            provisioned_iops=5000,
            average_iops=100,
            average_throughput_mbps=15,
            burst_balance_percent=100,
        ),
        VolumeMetrics(
            volume_id="vol-004",
            tier="gp3",
            size_gib=100,
            provisioned_iops=3000,
            average_iops=2000,
            average_throughput_mbps=15,
            burst_balance_percent=100,
        ),
    ]

    results = optimize_many(metrics_list)
    assert len(results) == 2
    assert all(isinstance(item, OptimizationRecommendation) for item in results)
