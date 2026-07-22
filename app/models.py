"""ORM models: flagged connections, the risk catalog, and ingestion performance history."""
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String

from app.database import Base


class RiskCategory(Base):
    __tablename__ = "risk_categories"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String, unique=True, index=True, nullable=False)
    category = Column(String, nullable=False)
    risk_level = Column(String, nullable=False)  # Critical | High | Medium | Low


class AnomalyEvent(Base):
    __tablename__ = "anomaly_events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True, nullable=False)
    source_ip = Column(String, nullable=False)
    destination_ip = Column(String, nullable=False)
    destination_domain = Column(String, index=True, nullable=False)
    bytes_transferred = Column(Integer, nullable=False)
    protocol = Column(String, nullable=False)
    category = Column(String, nullable=False)
    risk_level = Column(String, index=True, nullable=False)
    action = Column(String, default="Pending", nullable=False)  # Pending | Blocked | Acknowledged
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class PerformanceMetric(Base):
    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, index=True, nullable=False)
    total_records = Column(Integer, nullable=False)
    anomalies_found = Column(Integer, nullable=False)
    duration_ms = Column(Float, nullable=False)
    records_per_second = Column(Float, nullable=False)
    peak_memory_mb = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
