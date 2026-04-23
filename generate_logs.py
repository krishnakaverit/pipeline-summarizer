import json
import random
from datetime import datetime, timedelta

pipelines = ["customer_etl", "sales_report", "inventory_sync", "user_analytics", "payment_reconciliation"]
statuses = ["success", "success", "success", "failed", "failed", "warning"]
errors = [
    "TimeoutError: connection timed out after 30s",
    "FileNotFoundError: source file missing",
    "DatabaseError: could not connect to postgres",
    "MemoryError: out of memory during transform",
    "ValueError: null values found in required column",
]

logs = []
base_time = datetime.now()

for i in range(100):
    status = random.choice(statuses)
    log = {
        "id": i + 1,
        "pipeline": random.choice(pipelines),
        "status": status,
        "timestamp": (base_time - timedelta(hours=random.randint(1, 72))).strftime("%Y-%m-%d %H:%M:%S"),
        "duration_seconds": random.randint(10, 600),
        "error": random.choice(errors) if status == "failed" else None,
        "rows_processed": random.randint(100, 50000) if status != "failed" else 0,
    }
    logs.append(log)

with open("logs.json", "w") as f:
    json.dump(logs, f, indent=2)

print(f"Generated {len(logs)} logs and saved to logs.json")