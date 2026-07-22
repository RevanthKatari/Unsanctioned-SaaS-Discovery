# Shadow Network Log Analyzer

A local network log analyzer that ingests firewall/DNS traffic logs, flags connections to
unsanctioned external apps (Shadow SaaS / Shadow AI), and surfaces them on a dark,
glassmorphic security dashboard.

## Stack
- **Backend:** FastAPI + SQLAlchemy (SQLite)
- **Data processing:** Pandas
- **Frontend:** HTML5 + Tailwind CSS (CDN) + Chart.js + vanilla JS
- **Perf tracking:** custom `@benchmark` decorator (wall-clock time + peak memory via `tracemalloc`)

## Setup

```bash
cd shadow-saas-analyzer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Generate synthetic log data

```bash
python data/log_generator.py
```

Writes `data/firewall_logs.csv` with 100,000 rows of simulated firewall/DNS traffic,
about 8% of which hit domains listed in `data/risk_matrix.json`.

## Run the app

```bash
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000 — use the "Upload CSV" button in the sidebar to ingest
`data/firewall_logs.csv` (or any CSV with the same columns) and populate the dashboard.

## CSV schema expected by the ingestion engine

```
timestamp, source_ip, destination_ip, destination_domain, bytes_transferred, protocol
```

## API

- `POST /api/upload-log` — ingest a CSV, returns a run summary (records, anomalies, duration, records/sec, peak memory)
- `GET /api/anomalies?page=&page_size=&risk_level=&sort_by=&order=` — paginated flagged connections
- `PATCH /api/anomalies/{id}/action` — set `Blocked` / `Acknowledged` / `Pending`
- `GET /api/metrics/summary` — top-line dashboard metrics
- `GET /api/metrics/performance` — ingestion run history (Records/sec benchmark)
- `GET /api/metrics/anomalies-over-time` — daily anomaly counts for the time-series chart

## Editing the risk matrix

Add/edit entries in `data/risk_matrix.json`:

```json
"newdomain.com": {"category": "Shadow AI", "risk_level": "High"}
```
