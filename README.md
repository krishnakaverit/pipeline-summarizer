# 🔭 LLM-Powered Pipeline Observability Tool

A production-grade, RAG-based data observability tool that summarizes ETL pipeline logs, detects anomalies, and answers natural language queries using OpenAI GPT and ChromaDB.

## 🚀 Live Demo
👉 https://pipeline-observability.streamlit.app

## ✨ Features
- 🔍 Natural language querying — ask "which pipelines failed?" in plain English
- 🤖 AI-powered summaries — root cause analysis using OpenAI GPT-3.5
- 💬 Conversational chat — ask follow-up questions with memory
- 📊 Pipeline health dashboard — per-pipeline success rates and error breakdown
- 📈 Trend charts — daily runs, failure rates, error distribution using Plotly
- 🚨 Automatic anomaly detection — severity classification with AI action plans
- 📁 Custom log upload — upload any JSON log file for instant analysis
- 📅 Date range filtering — filter all views by date
- 📥 Export summaries — download AI reports as text files

## 🛠️ Tech Stack
- Python — Core language
- ChromaDB — Vector database for semantic log search
- LangChain — RAG pipeline orchestration
- OpenAI GPT-3.5 — Natural language summarization
- Streamlit — Interactive web dashboard
- Plotly — Interactive charts and visualizations

## 📁 Project Structure
- app.py — Main Streamlit dashboard
- generate_logs.py — Synthetic Airflow-style log generator
- store_logs.py — Embeds and stores logs in ChromaDB
- query_logs.py — Plain English querying of logs
- summarize.py — OpenAI-powered summarization
- logs.json — Generated pipeline logs
- sample_logs.json — Sample logs for testing upload feature
- .env — API keys (not committed)

## ⚙️ Setup Instructions

Step 1 — Clone the repository
git clone https://github.com/krishnakaverit/pipeline-summarizer.git
cd pipeline-summarizer

Step 2 — Create a virtual environment
python -m venv venv
venv\Scripts\activate

Step 3 — Install dependencies
pip install langchain langchain-openai langchain-chroma chromadb openai streamlit python-dotenv plotly pandas streamlit-extras

Step 4 — Create a .env file and add your OpenAI API key
OPENAI_API_KEY=your-key-here

Step 5 — Generate logs and store in ChromaDB
python generate_logs.py
python store_logs.py

Step 6 — Run the app
streamlit run app.py

## 💡 How It Works
1. ETL pipeline logs are embedded as vectors and stored in ChromaDB
2. User asks a question in plain English
3. ChromaDB retrieves the most semantically relevant logs using vector similarity search
4. OpenAI GPT summarizes findings with root cause analysis and recommendations
5. Anomaly detection automatically flags high failure rates and recurring errors

## 🎯 Use Cases
- Monitor ETL pipeline health across multiple pipelines
- Quickly identify recurring errors and their root causes
- Get plain-English summaries instead of reading raw logs
- Detect anomalies before they become critical issues

