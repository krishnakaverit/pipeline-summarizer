# 🔭 LLM-Powered Pipeline Observability Tool

A RAG-based data observability tool that summarizes ETL pipeline logs and detects anomalies using natural language queries.

## 🚀 Features
- Natural language querying of pipeline logs ("which pipelines failed?")
- AI-powered root cause analysis using OpenAI GPT
- Automatic anomaly detection with severity levels
- Pipeline health dashboard with per-pipeline breakdown
- Color-coded log viewer (success/warning/failure)
- Smart metadata filtering for precise results

## 🛠️ Tech Stack
- **Python** — core language
- **ChromaDB** — vector database for log storage and semantic search
- **LangChain** — RAG pipeline orchestration
- **OpenAI GPT-3.5** — natural language summarization
- **Streamlit** — interactive web dashboard

## 📁 Project Structure

pipeline-summarizer/
├── generate_logs.py   # Generates synthetic Airflow-style ETL logs
├── store_logs.py      # Embeds and stores logs in ChromaDB
├── query_logs.py      # Plain English querying of logs
├── summarize.py       # OpenAI-powered summarization
├── app.py             # Streamlit dashboard
├── logs.json          # Generated pipeline logs
└── .env               # API keys (not committed)

## ⚙️ Setup Instructions

1. Clone the repository
2. Create a virtual environment:
```bash
   python -m venv venv
   venv\Scripts\activate
```
3. Install dependencies:
```bash
   pip install langchain langchain-openai langchain-chroma chromadb openai streamlit python-dotenv
```
4. Create a `.env` file and add your OpenAI API key:

OPENAI_API_KEY=your-key-here

5. Generate logs and store in ChromaDB:
```bash
   python generate_logs.py
   python store_logs.py
```
6. Run the app:
```bash
   streamlit run app.py
```