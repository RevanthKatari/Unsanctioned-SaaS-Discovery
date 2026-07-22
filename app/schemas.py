"""Pydantic response/request schemas for the API layer."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AnomalyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: datetime
    source_ip: str
    destination_ip: str
    destination_domain: str
    bytes_transferred: int
    protocol: str
    category: str
    risk_level: str
    action: str


class PaginatedAnomalies(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[AnomalyOut]


class ActionUpdate(BaseModel):
    action: str  # "Blocked" | "Acknowledged"


class UploadSummary(BaseModel):
    run_id: str
    total_records: int
    anomalies_found: int
    duration_ms: float
    records_per_second: float
    peak_memory_mb: float


class MetricsSummary(BaseModel):
    total_logs_scanned: int
    total_anomalies: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    last_processing_time_ms: Optional[float]
    risk_breakdown: dict[str, int]


class PerformanceHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    run_id: str
    total_records: int
    anomalies_found: int
    duration_ms: float
    records_per_second: float
    peak_memory_mb: float
    created_at: datetime
