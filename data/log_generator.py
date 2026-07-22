"""Generates a synthetic firewall/DNS traffic log CSV for the Shadow SaaS analyzer demo."""
import csv
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).parent
RISK_MATRIX_PATH = DATA_DIR / "risk_matrix.json"
OUTPUT_PATH = DATA_DIR / "firewall_logs.csv"

APPROVED_DOMAINS = [
    "okta.com", "microsoft.com", "office.com", "salesforce.com",
    "workday.com", "internal.corp.local", "sharepoint.com", "zendesk.com",
    "atlassian.net", "servicenow.com",
]

PROTOCOLS = ["TCP", "UDP", "HTTPS", "DNS"]


def _random_internal_ip() -> str:
    return f"10.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"


def _random_external_ip() -> str:
    return f"{random.randint(20, 220)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"


def generate_logs(num_rows: int = 100_000, shadow_ratio: float = 0.08) -> Path:
    """Writes `num_rows` synthetic log rows to firewall_logs.csv and returns its path."""
    with open(RISK_MATRIX_PATH) as f:
        shadow_domains = list(json.load(f).keys())

    start_time = datetime.now() - timedelta(days=7)
    rows_written = 0

    with open(OUTPUT_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "timestamp", "source_ip", "destination_ip",
            "destination_domain", "bytes_transferred", "protocol",
        ])

        for _ in range(num_rows):
            ts = start_time + timedelta(seconds=random.randint(0, 7 * 24 * 3600))
            is_shadow = random.random() < shadow_ratio
            domain = random.choice(shadow_domains) if is_shadow else random.choice(APPROVED_DOMAINS)
            row = [
                ts.strftime("%Y-%m-%d %H:%M:%S"),
                _random_internal_ip(),
                _random_external_ip(),
                domain,
                random.randint(512, 50_000_000),
                random.choice(PROTOCOLS),
            ]
            writer.writerow(row)
            rows_written += 1

    return OUTPUT_PATH


if __name__ == "__main__":
    path = generate_logs()
    print(f"Wrote synthetic log file: {path}")
