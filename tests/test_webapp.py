"""Tests for the web UI."""

from __future__ import annotations

import io
import json
from typing import Dict, Iterable, Tuple
from urllib.parse import urlencode
from wsgiref.util import setup_testing_defaults

from aws_ebs_optimizer import webapp


def call_application(
    method: str = "GET", path: str = "/", data: Dict[str, str] | None = None
) -> Tuple[str, Dict[str, str], bytes]:
    """Invoke the WSGI application and return response components."""

    environ = {}
    setup_testing_defaults(environ)
    environ["REQUEST_METHOD"] = method
    environ["PATH_INFO"] = path

    if data is not None:
        encoded = urlencode(data).encode("utf-8")
        environ["CONTENT_LENGTH"] = str(len(encoded))
        environ["wsgi.input"] = io.BytesIO(encoded)

    status_headers: Dict[str, str] = {}

    def start_response(status: str, headers: Iterable[Tuple[str, str]]):
        status_headers["status"] = status
        status_headers.update(dict(headers))

    body = b"".join(webapp.application(environ, start_response))
    return status_headers["status"], status_headers, body


def test_get_renders_form():
    status, headers, body = call_application()

    assert status == "200 OK"
    assert headers["Content-Type"].startswith("text/html")
    html = body.decode("utf-8")
    assert "AWS EBS Optimizer" in html
    assert "textarea" in html


def test_post_returns_recommendations():
    payload = json.dumps(
        [
            {
                "volume_id": "vol-abc",
                "tier": "gp2",
                "size_gib": 200,
                "provisioned_iops": 3000,
                "average_iops": 250,
                "average_throughput_mbps": 40,
                "burst_balance_percent": 10,
            }
        ]
    )
    status, _, body = call_application(
        method="POST", data={"metrics_json": payload}
    )

    assert status == "200 OK"
    html = body.decode("utf-8")
    assert "Recommendations" in html
    assert "vol-abc" in html


def test_invalid_json_returns_error():
    status, _, body = call_application(method="POST", data={"metrics_json": "{"})

    assert status.startswith("400")
    html = body.decode("utf-8")
    assert "error" in html.lower()
