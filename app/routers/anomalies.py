"""Anomalies endpoint: paginated, filterable, sortable list of flagged connections."""
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AnomalyEvent
from app.schemas import ActionUpdate, AnomalyOut, PaginatedAnomalies

router = APIRouter(prefix="/api", tags=["anomalies"])

SORTABLE_FIELDS = {
    "timestamp": AnomalyEvent.timestamp,
    "risk_level": AnomalyEvent.risk_level,
    "bytes_transferred": AnomalyEvent.bytes_transferred,
}


@router.get("/anomalies", response_model=PaginatedAnomalies)
def list_anomalies(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
    risk_level: Optional[str] = Query(None, description="Filter: Critical | High | Medium | Low"),
    sort_by: Literal["timestamp", "risk_level", "bytes_transferred"] = "timestamp",
    order: Literal["asc", "desc"] = "desc",
    db: Session = Depends(get_db),
) -> PaginatedAnomalies:
    q = db.query(AnomalyEvent)
    if risk_level:
        q = q.filter(AnomalyEvent.risk_level == risk_level)

    total = q.count()
    sort_col = SORTABLE_FIELDS[sort_by]
    q = q.order_by(desc(sort_col) if order == "desc" else asc(sort_col))
    items = q.offset((page - 1) * page_size).limit(page_size).all()

    return PaginatedAnomalies(total=total, page=page, page_size=page_size, items=items)


@router.patch("/anomalies/{anomaly_id}/action", response_model=AnomalyOut)
def update_action(anomaly_id: int, payload: ActionUpdate, db: Session = Depends(get_db)) -> AnomalyOut:
    if payload.action not in {"Blocked", "Acknowledged", "Pending"}:
        raise HTTPException(status_code=400, detail="action must be Blocked, Acknowledged, or Pending")

    event = db.query(AnomalyEvent).filter(AnomalyEvent.id == anomaly_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Anomaly not found")

    event.action = payload.action
    db.commit()
    db.refresh(event)
    return event
