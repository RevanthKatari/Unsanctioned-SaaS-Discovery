"""FastAPI application entry point for the Shadow Network Log Analyzer."""
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.routers import anomalies, metrics, upload

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Shadow Network Log Analyzer")

app.include_router(upload.router)
app.include_router(anomalies.router)
app.include_router(metrics.router)

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/")
def dashboard() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")
