"""Reporting helpers for calculating performance metrics and formatting execution summaries."""

from __future__ import annotations

import statistics
from typing import Any


def calculate_latency_metrics(latencies: list[float]) -> dict[str, float]:
    """Calculate key latency statistics (min, max, mean, median, p95)."""
    if not latencies:
        return {"count": 0, "min": 0.0, "max": 0.0, "mean": 0.0, "median": 0.0, "p95": 0.0}

    sorted_lats = sorted(latencies)
    n = len(sorted_lats)
    p95_idx = int(n * 0.95) if n > 1 else 0

    return {
        "count": float(n),
        "min": round(min(sorted_lats), 4),
        "max": round(max(sorted_lats), 4),
        "mean": round(statistics.mean(sorted_lats), 4),
        "median": round(statistics.median(sorted_lats), 4),
        "p95": round(sorted_lats[p95_idx], 4),
    }


def format_summary_table(metrics: dict[str, Any]) -> str:
    """Format performance metrics as a markdown table."""
    lines = [
        "| Metric | Value |",
        "|---|---|",
        f"| Request Count | {int(metrics.get('count', 0))} |",
        f"| Min Latency | {metrics.get('min', 0):.4f}s |",
        f"| Max Latency | {metrics.get('max', 0):.4f}s |",
        f"| Mean Latency | {metrics.get('mean', 0):.4f}s |",
        f"| Median Latency | {metrics.get('median', 0):.4f}s |",
        f"| 95th Percentile | {metrics.get('p95', 0):.4f}s |",
    ]
    return "\n".join(lines)
