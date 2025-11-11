"""Tests for the CLI entry points."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from aws_ebs_optimizer import cli


@pytest.fixture()
def metrics_file(tmp_path: Path) -> Path:
    """Return a temporary metrics file for testing."""

    path = tmp_path / "metrics.json"
    payload = [
        {
            "volume_id": "vol-test",
            "tier": "gp2",
            "size_gib": 200,
            "provisioned_iops": 3000,
            "average_iops": 250,
            "average_throughput_mbps": 40,
            "burst_balance_percent": 10,
        }
    ]
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_main_prints_recommendations(capsys, metrics_file: Path) -> None:
    """Running the CLI prints human-readable recommendations."""

    exit_code = cli.main([str(metrics_file)])

    assert exit_code == 0
    captured = capsys.readouterr().out
    assert "Volume: vol-test" in captured
    assert "Action" in captured


def test_main_writes_output_file(tmp_path: Path, metrics_file: Path) -> None:
    """Passing --output writes JSON recommendations to the provided path."""

    output_path = tmp_path / "recs.json"

    exit_code = cli.main([str(metrics_file), "--output", str(output_path)])

    assert exit_code == 0
    data = json.loads(output_path.read_text(encoding="utf-8"))
    assert data[0]["volume_id"] == "vol-test"


def test_main_reports_errors(capsys, tmp_path: Path) -> None:
    """Failures are reported to stderr and yield a non-zero exit code."""

    missing = tmp_path / "missing.json"

    exit_code = cli.main([str(missing)])

    assert exit_code == 1
    captured = capsys.readouterr()
    assert "error" in captured.err.lower()


def test_serve_option_invokes_web_ui(monkeypatch) -> None:
    """The --serve option starts the web UI using the provided host/port."""

    called: dict[str, tuple[str, int]] = {}

    def fake_serve(*, host: str, port: int) -> None:  # pragma: no cover - small helper
        called["args"] = (host, port)

    monkeypatch.setattr(cli, "serve_ui", fake_serve)

    exit_code = cli.main(["--serve", "--host", "0.0.0.0", "--port", "9000"])

    assert exit_code == 0
    assert called["args"] == ("0.0.0.0", 9000)
