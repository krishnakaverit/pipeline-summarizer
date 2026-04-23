import chromadb
from chromadb.utils import embedding_functions
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load API key from .env file
load_dotenv()
client_ai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Connect to ChromaDB
client_db = chromadb.PersistentClient(path="./chroma_db")
ef = embedding_functions.DefaultEmbeddingFunction()
collection = client_db.get_or_create_collection(
    name="pipeline_logs",
    embedding_function=ef
)

def ask_and_summarize(question):
    print(f"\n🔍 Question: {question}")
    print("-" * 50)

    # Get relevant logs from ChromaDB
    results = collection.query(
        query_texts=[question],
        n_results=5
    )
    logs = "\n".join(results["documents"][0])

    # Ask OpenAI to summarize
    response = client_ai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a data engineer assistant. Summarize ETL pipeline logs clearly and highlight any issues."},
            {"role": "user", "content": f"Question: {question}\n\nRelevant logs:\n{logs}\n\nPlease summarize what you see in plain English."}
        ]
    )

    print(response.choices[0].message.content)

# Test it out
ask_and_summarize("which pipelines failed and why?")
ask_and_summarize("give me a health summary of all pipelines")