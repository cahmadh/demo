# AWS EBS Optimizer

AWS EBS Optimizer is a lightweight command line tool that analyzes utilization
metrics for Amazon Elastic Block Store (EBS) volumes and recommends potential
cost or performance optimizations. The heuristics emulate common AWS guidance so
the tool can be run locally without cloud credentials.

## Features

* Simple Python package with reusable optimization logic.
* CLI that consumes a JSON file containing volume metrics and prints
  human-readable recommendations or writes them to disk.
* Browser-based UI for experimenting with recommendations without using the CLI.
* Sample dataset you can use to explore how the optimizer works.
* Unit tests that demonstrate expected recommendations for key scenarios.

## Getting Started

1. Create and activate a Python 3.10+ virtual environment.
2. Install the project in editable mode:

   ```bash
   pip install -e .
   ```

3. Run the optimizer against the sample dataset:

   ```bash
   python -m aws_ebs_optimizer.cli sample_data/volumes.json
   ```

   To save the output instead of printing it:

   ```bash
   python -m aws_ebs_optimizer.cli sample_data/volumes.json -o recommendations.json
   ```

4. Launch the interactive web interface:

   ```bash
   python -m aws_ebs_optimizer.webapp
   ```

   Then open <http://127.0.0.1:8000> in your browser. Paste your JSON metrics
   into the text area and submit the form to see recommendations rendered
   directly on the page. The server uses Python's built-in WSGI server, so it is
   intended for local use only.

## Running Tests

```bash
pytest
```

## Input Format

The optimizer expects a JSON file with a list of volume metric objects. Each
object should contain the following fields:

* `volume_id` – The AWS volume identifier.
* `tier` – The current EBS volume type (for example `gp2`, `gp3`, `io1`).
* `size_gib` – Provisioned capacity in GiB.
* `provisioned_iops` – Provisioned IOPS capacity.
* `average_iops` – Observed average IOPS during the assessment window.
* `average_throughput_mbps` – Observed throughput in MiB/s.
* `burst_balance_percent` – Burst balance percentage (for gp2 volumes).

## Packaging

A minimal `pyproject.toml` is included so the optimizer can be installed as a
package or distributed internally.
