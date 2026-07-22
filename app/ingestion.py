"""Business logic: Pandas-based log ingestion, risk cross-referencing, and performance tracking."""
from __future__ import annotations

import json
import time
import tracemalloc
import uuid
from dataclasses import dataclass
from functools import wraps
from pathlib import Path
from typing import Callable

import pandas as pd
from sqlalchemy.orm import Session

from app.models import AnomalyEvent, PerformanceMetric

RISK_MATRIX_PATH = Path(__file__).parent.parent / "data" / "risk_matrix.json"


@dataclass
class BenchmarkResult:
    """Captures timing/memory stats for one ingestion run, plus the wrapped function's return value."""
    duration_ms: float
    peak_memory_mb: float
    result: object


def benchmark(func: Callable) -> Callable:
    """Decorator that measures wall-clock duration and peak memory for the wrapped call."""
    @wraps(func)
    def wrapper(*args, **kwargs) -> BenchmarkResult:
        tracemalloc.start()
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration_ms = (time.perf_counter() - start) * 1000
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        return BenchmarkResult(duration_ms=duration_ms, peak_memory_mb=peak / (1024 * 1024), result=result)
    return wrapper


def load_risk_matrix() -> dict:
    """Loads the domain -> {category, risk_level} lookup table."""
    with open(RISK_MATRIX_PATH) as f:
        return json.load(f)


@benchmark
def _process_dataframe(df: pd.DataFrame, risk_matrix: dict) -> pd.DataFrame:
    """Filters to flagged (unsanctioned) rows and attaches category/risk_level columns."""
    flagged = df[df["destination_domain"].isin(risk_matrix.keys())].copy()
    flagged["category"] = flagged["destination_domain"].map(lambda d: risk_matrix[d]["category"])
    flagged["risk_level"] = flagged["destination_domain"].map(lambda d: risk_matrix[d]["risk_level"])
    return flagged


def ingest_log_file(csv_path: str | Path, db: Session) -> dict:
    """Reads a firewall/DNS log CSV, flags unsanctioned domains, persists anomalies + a performance record.

    Returns a summary dict used directly by the /api/upload-log response.
    """
    risk_matrix = load_risk_matrix()
    df = pd.read_csv(csv_path, parse_dates=["timestamp"])
    total_records = len(df)

    bench = _process_dataframe(df, risk_matrix)
    flagged = bench.result

    events = [
        AnomalyEvent(
            timestamp=row.timestamp.to_pydatetime(),
            source_ip=row.source_ip,
            destination_ip=row.destination_ip,
            destination_domain=row.destination_domain,
            bytes_transferred=int(row.bytes_transferred),
            protocol=row.protocol,
            category=row.category,
            risk_level=row.risk_level,
        )
        for row in flagged.itertuples(index=False)
    ]
    db.bulk_save_objects(events)

    records_per_second = total_records / (bench.duration_ms / 1000) if bench.duration_ms > 0 else 0.0
    run_id = uuid.uuid4().hex[:12]
    metric = PerformanceMetric(
        run_id=run_id,
        total_records=total_records,
        anomalies_found=len(events),
        duration_ms=bench.duration_ms,
        records_per_second=records_per_second,
        peak_memory_mb=bench.peak_memory_mb,
    )
    db.add(metric)
    db.commit()

    return {
        "run_id": run_id,
        "total_records": total_records,
        "anomalies_found": len(events),
        "duration_ms": round(bench.duration_ms, 2),
        "records_per_second": round(records_per_second, 2),
        "peak_memory_mb": round(bench.peak_memory_mb, 2),
    }
