from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import json
import random
import chromadb
from chromadb.utils import embedding_functions

# --- Default args ---
default_args = {
    'owner': 'kaveri',
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

# --- Generate new logs ---
def generate_new_logs():
    pipelines = ["customer_etl", "sales_report", "inventory_sync", "user_analytics", "payment_reconciliation"]
    statuses = ["success", "success", "success", "failed", "failed", "warning"]
    errors = [
        "TimeoutError: connection timed out after 30s",
        "FileNotFoundError: source file missing",
        "DatabaseError: could not connect to postgres",
        "MemoryError: out of memory during transform",
        "ValueError: null values found in required column",
    ]

    # Load existing logs
    try:
        with open("/opt/airflow/logs.json", "r") as f:
            logs = json.load(f)
    except:
        logs = []

    # Generate 10 new logs
    start_id = len(logs) + 1
    for i in range(10):
        status = random.choice(statuses)
        log = {
            "id": start_id + i,
            "pipeline": random.choice(pipelines),
            "status": status,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "duration_seconds": random.randint(10, 600),
            "error": random.choice(errors) if status == "failed" else None,
            "rows_processed": random.randint(100, 50000) if status != "failed" else 0,
        }
        logs.append(log)

    # Save updated logs
    with open("/opt/airflow/logs.json", "w") as f:
        json.dump(logs, f, indent=2)

    print(f"Generated 10 new logs. Total: {len(logs)}")

# --- Store new logs in ChromaDB ---
def store_new_logs():
    with open("/opt/airflow/logs.json", "r") as f:
        logs = json.load(f)

    client = chromadb.PersistentClient(path="/opt/airflow/chroma_db")
    ef = embedding_functions.DefaultEmbeddingFunction()
    collection = client.get_or_create_collection(
        name="pipeline_logs",
        embedding_function=ef
    )

    # Get existing IDs
    existing = collection.get()
    existing_ids = set(existing["ids"])

    # Add only new logs
    new_docs = []
    new_ids = []
    new_metas = []

    for log in logs:
        log_id = str(log["id"])
        if log_id not in existing_ids:
            if log["status"] == "failed":
                text = f"Pipeline {log['pipeline']} FAILED at {log['timestamp']} with error: {log['error']}"
            elif log["status"] == "warning":
                text = f"Pipeline {log['pipeline']} completed with WARNING at {log['timestamp']}, processed {log['rows_processed']} rows"
            else:
                text = f"Pipeline {log['pipeline']} succeeded at {log['timestamp']}, processed {log['rows_processed']} rows in {log['duration_seconds']} seconds"

            new_docs.append(text)
            new_ids.append(log_id)
            new_metas.append({"pipeline": log["pipeline"], "status": log["status"]})

    if new_docs:
        collection.add(documents=new_docs, metadatas=new_metas, ids=new_ids)
        print(f"Stored {len(new_docs)} new logs in ChromaDB!")
    else:
        print("No new logs to store.")

# --- DAG definition ---
with DAG(
    dag_id="pipeline_log_ingestion",
    default_args=default_args,
    description="Automatically generate and store pipeline logs every hour",
    schedule_interval="@hourly",
    start_date=datetime(2026, 4, 23),
    catchup=False,
    tags=["observability", "etl", "llm"],
) as dag:

    generate_task = PythonOperator(
        task_id="generate_new_logs",
        python_callable=generate_new_logs,
    )

    store_task = PythonOperator(
        task_id="store_logs_in_chromadb",
        python_callable=store_new_logs,
    )

    generate_task >> store_task