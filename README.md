# 🔭 LLM-Powered Pipeline Observability Tool

A production-grade, end-to-end data observability platform that automatically ingests ETL pipeline logs via Apache Airflow, stores them as vector embeddings in ChromaDB, and enables natural language querying and anomaly detection using OpenAI GPT.

## 🚀 Live Demo
👉 https://pipeline-observability.streamlit.app

## 🏗️ Architecture
Airflow DAG (runs every hour)
→ Generates new pipeline logs automatically
→ Stores in ChromaDB as vector embeddings
→ Streamlit Dashboard queries with OpenAI GPT
→ Real-time anomaly detection and plain-English summaries

## ✨ Features
- ⏰ Automated log ingestion via Apache Airflow DAGs running every hour
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
- Apache Airflow — Automated hourly pipeline log ingestion (DAG orchestration)
- ChromaDB — Vector database for semantic log search
- LangChain — RAG pipeline orchestration
- OpenAI GPT-3.5 — Natural language summarization and root cause analysis
- Streamlit — Interactive web dashboard
- Plotly — Interactive charts and visualizations
- Docker — Containerized Airflow deployment

## 📁 Project Structure
- app.py — Main Streamlit dashboard
- generate_logs.py — Synthetic Airflow-style log generator
- store_logs.py — Embeds and stores logs in ChromaDB
- query_logs.py — Plain English querying of logs
- summarize.py — OpenAI-powered summarization
- logs.json — Generated pipeline logs
- sample_logs.json — Sample logs for testing upload feature
- requirements.txt — Python dependencies
- airflow/
  - Dockerfile — Custom Airflow image with ChromaDB
  - docker-compose.yml — Airflow container setup
  - dags/pipeline_log_dag.py — Hourly log ingestion DAG

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

Step 6 — Run the Streamlit app
streamlit run app.py

Step 7 — Start Airflow (requires Docker Desktop)
cd airflow
docker-compose up -d

Step 8 — Access Airflow dashboard
Go to http://localhost:8080
Username: admin
Enable the pipeline_log_ingestion DAG

## 💡 How It Works
1. Apache Airflow runs the pipeline_log_ingestion DAG every hour automatically
2. The DAG generates 10 new realistic ETL pipeline logs
3. Logs are embedded as vectors and stored in ChromaDB
4. User asks a question in plain English on the Streamlit dashboard
5. ChromaDB retrieves the most semantically relevant logs
6. OpenAI GPT summarizes findings with root cause analysis and recommendations
7. Anomaly detection automatically flags high failure rates and recurring errors

## 🎯 Use Cases
- Monitor ETL pipeline health across multiple pipelines in real-time
- Quickly identify recurring errors and their root causes
- Get plain-English summaries instead of reading raw logs
- Detect anomalies before they become critical issues
- Simulate production-grade data observability like Monte Carlo or DataDog

## 👩‍💻 Author
Krishna Kaveri T
- LinkedIn: linkedin.com/in/krishna-kaveri-t-833a1120a
- Email: krishnakaverit@gmail.com
- GitHub: github.com/krishnakaverit