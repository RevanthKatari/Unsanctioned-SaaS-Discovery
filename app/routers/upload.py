"""Upload endpoint: accepts a firewall/DNS log CSV and triggers ingestion."""
import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.ingestion import ingest_log_file
from app.schemas import UploadSummary

router = APIRouter(prefix="/api", tags=["upload"])


@router.post("/upload-log", response_model=UploadSummary)
def upload_log(file: UploadFile, db: Session = Depends(get_db)) -> UploadSummary:
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are accepted")

    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = Path(tmp.name)

    try:
        summary = ingest_log_file(tmp_path, db)
    finally:
        tmp_path.unlink(missing_ok=True)

    return UploadSummary(**summary)
