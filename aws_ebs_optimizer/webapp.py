"""Simple web front end for the AWS EBS Optimizer."""

from __future__ import annotations

import html
import io
import json
from typing import Iterable
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

from .io_utils import deserialize_metrics, format_recommendations
from .optimizer import optimize_many


PAGE_TEMPLATE = """<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <title>AWS EBS Optimizer</title>
    <style>
      body {{ font-family: system-ui, sans-serif; margin: 2rem; max-width: 960px; }}
      textarea {{ width: 100%; min-height: 240px; font-family: monospace; }}
      .error {{ color: #b00020; margin-bottom: 1rem; }}
      .results {{ margin-top: 2rem; padding: 1rem; border: 1px solid #ccc; border-radius: 6px; }}
      pre {{ white-space: pre-wrap; word-break: break-word; }}
      form {{ display: grid; gap: 1rem; }}
      button {{ width: 200px; padding: 0.75rem; font-size: 1rem; }}
    </style>
  </head>
  <body>
    <h1>AWS EBS Optimizer</h1>
    <p>Paste AWS EBS volume metrics as JSON into the text area and submit to receive optimization recommendations.</p>
    {error_html}
    <form method=\"post\">
      <label for=\"metrics_json\">Volume metrics JSON</label>
      <textarea id=\"metrics_json\" name=\"metrics_json\" required>{metrics_json}</textarea>
      <button type=\"submit\">Analyze volumes</button>
    </form>
    {results_html}
  </body>
</html>
"""


def _render_page(metrics_json: str, results: str | None = None, error: str | None = None) -> Iterable[bytes]:
    """Render the HTML page."""

    error_html = f'<div class="error">{html.escape(error)}</div>' if error else ""
    results_html = (
        f'<div class="results"><h2>Recommendations</h2><pre>{html.escape(results)}</pre></div>'
        if results
        else ""
    )

    page_html = PAGE_TEMPLATE.format(
        metrics_json=html.escape(metrics_json, quote=False),
        results_html=results_html,
        error_html=error_html,
    )

    yield page_html.encode("utf-8")


def application(environ, start_response):  # type: ignore[override]
    """WSGI application callable that serves the optimizer UI."""

    method = environ.get("REQUEST_METHOD", "GET").upper()

    if method == "POST":
        try:
            length = int(environ.get("CONTENT_LENGTH", "0"))
        except ValueError:
            length = 0
        body = environ.get("wsgi.input", io.BytesIO()).read(length)
        params = parse_qs(body.decode("utf-8"))
        metrics_json = params.get("metrics_json", [""])[0]

        try:
            raw_payload = json.loads(metrics_json)
            if not isinstance(raw_payload, list):
                raise ValueError("Expected a JSON array of metric objects.")
            metrics = deserialize_metrics(raw_payload)
            recommendations = optimize_many(metrics)
            formatted = format_recommendations(recommendations)
            start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
            return list(_render_page(metrics_json, formatted))
        except Exception as exc:  # pylint: disable=broad-except
            start_response("400 Bad Request", [("Content-Type", "text/html; charset=utf-8")])
            return list(_render_page(metrics_json, None, str(exc)))

    # Default GET handler
    start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
    sample_metrics = json.dumps(
        [
            {
                "volume_id": "vol-0123456789abcdef0",
                "tier": "gp2",
                "size_gib": 200,
                "provisioned_iops": 3000,
                "average_iops": 250,
                "average_throughput_mbps": 40,
                "burst_balance_percent": 18,
            }
        ],
        indent=2,
    )
    return list(_render_page(sample_metrics))


def serve(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Launch a development server serving the optimizer UI."""

    with make_server(host, port, application) as httpd:
        print(f"Serving AWS EBS Optimizer UI at http://{host}:{port}")
        httpd.serve_forever()


def run(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Backward-compatible alias for :func:`serve`."""

    serve(host=host, port=port)


if __name__ == "__main__":  # pragma: no cover - manual entry point
    run()
