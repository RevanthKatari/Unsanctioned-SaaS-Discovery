"""Metrics endpoints: top-line dashboard summary and ingestion performance history."""
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AnomalyEvent, PerformanceMetric
from app.schemas import MetricsSummary, PerformanceHistoryItem

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get("/summary", response_model=MetricsSummary)
def metrics_summary(db: Session = Depends(get_db)) -> MetricsSummary:
    risk_counts = dict(
        db.query(AnomalyEvent.risk_level, func.count(AnomalyEvent.id))
        .group_by(AnomalyEvent.risk_level)
        .all()
    )
    total_anomalies = sum(risk_counts.values())
    total_logs_scanned = db.query(func.sum(PerformanceMetric.total_records)).scalar() or 0
    last_metric = db.query(PerformanceMetric).order_by(PerformanceMetric.created_at.desc()).first()

    return MetricsSummary(
        total_logs_scanned=total_logs_scanned,
        total_anomalies=total_anomalies,
        critical_count=risk_counts.get("Critical", 0),
        high_count=risk_counts.get("High", 0),
        medium_count=risk_counts.get("Medium", 0),
        low_count=risk_counts.get("Low", 0),
        last_processing_time_ms=last_metric.duration_ms if last_metric else None,
        risk_breakdown=risk_counts,
    )


@router.get("/performance", response_model=list[PerformanceHistoryItem])
def performance_history(limit: int = 20, db: Session = Depends(get_db)) -> list[PerformanceHistoryItem]:
    return (
        db.query(PerformanceMetric)
        .order_by(PerformanceMetric.created_at.desc())
        .limit(limit)
        .all()
    )


@router.get("/anomalies-over-time")
def anomalies_over_time(db: Session = Depends(get_db)) -> list[dict]:
    """Daily anomaly counts, used to drive the dashboard's time-series chart."""
    rows = (
        db.query(
            func.date(AnomalyEvent.timestamp).label("day"),
            func.count(AnomalyEvent.id).label("count"),
        )
        .group_by("day")
        .order_by("day")
        .all()
    )
    return [{"day": r.day, "count": r.count} for r in rows]
