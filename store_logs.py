import json
import chromadb
from chromadb.utils import embedding_functions

# Load logs
with open("logs.json", "r") as f:
    logs = json.load(f)

# Setup ChromaDB
client = chromadb.PersistentClient(path="./chroma_db")

# Use default embedding function
ef = embedding_functions.DefaultEmbeddingFunction()

# Create a collection (like a table)
collection = client.get_or_create_collection(
    name="pipeline_logs",
    embedding_function=ef
)

# Store each log
documents = []
metadatas = []
ids = []

for log in logs:
    # Convert log to a readable sentence
    if log["status"] == "failed":
        text = f"Pipeline {log['pipeline']} FAILED at {log['timestamp']} with error: {log['error']}"
    elif log["status"] == "warning":
        text = f"Pipeline {log['pipeline']} completed with WARNING at {log['timestamp']}, processed {log['rows_processed']} rows"
    else:
        text = f"Pipeline {log['pipeline']} succeeded at {log['timestamp']}, processed {log['rows_processed']} rows in {log['duration_seconds']} seconds"

    documents.append(text)
    metadatas.append({"pipeline": log["pipeline"], "status": log["status"]})
    ids.append(str(log["id"]))

# Add to ChromaDB
collection.add(documents=documents, metadatas=metadatas, ids=ids)

print(f"Stored {len(documents)} logs in ChromaDB!")