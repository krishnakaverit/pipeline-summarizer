import chromadb
from chromadb.utils import embedding_functions

# Connect to ChromaDB
client = chromadb.PersistentClient(path="./chroma_db")
ef = embedding_functions.DefaultEmbeddingFunction()

collection = client.get_or_create_collection(
    name="pipeline_logs",
    embedding_function=ef
)

# Ask questions in plain English
questions = [
    "which pipelines failed?",
    "show me database connection errors",
    "which pipelines processed the most rows?",
]

for question in questions:
    print(f"\n🔍 Question: {question}")
    print("-" * 50)
    
    results = collection.query(
        query_texts=[question],
        n_results=3
    )
    
    for doc in results["documents"][0]:
        print(f"  → {doc}")