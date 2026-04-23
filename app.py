import streamlit as st
import chromadb
from chromadb.utils import embedding_functions
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from collections import defaultdict

load_dotenv()
client_ai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
client_db = chromadb.PersistentClient(path="./chroma_db")
ef = embedding_functions.DefaultEmbeddingFunction()
collection = client_db.get_or_create_collection(
    name="pipeline_logs",
    embedding_function=ef
)

with open("logs.json", "r") as f:
    logs = json.load(f)

# --- Stats ---
total = len(logs)
failed = [l for l in logs if l["status"] == "failed"]
success = [l for l in logs if l["status"] == "success"]
warning = [l for l in logs if l["status"] == "warning"]

# Per-pipeline stats
pipeline_stats = defaultdict(lambda: {"success": 0, "failed": 0, "warning": 0, "errors": []})
for l in logs:
    pipeline_stats[l["pipeline"]][l["status"]] += 1
    if l["error"]:
        pipeline_stats[l["pipeline"]]["errors"].append(l["error"])

# --- Page Config ---
st.set_page_config(page_title="Pipeline Observability", page_icon="🔭", layout="wide")

st.title("🔭 LLM-Powered Pipeline Observability")
st.caption("Real-time anomaly detection and natural language querying of ETL pipeline logs")

# --- Top Stats ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Runs", total)
col2.metric("✅ Successful", len(success), delta=f"{round(len(success)/total*100)}%")
col3.metric("❌ Failed", len(failed), delta=f"-{round(len(failed)/total*100)}%", delta_color="inverse")
col4.metric("⚠️ Warnings", len(warning))

st.divider()

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["🔍 Ask AI", "📊 Pipeline Health", "🚨 Anomalies"])

# ===================== TAB 1: ASK AI =====================
with tab1:
    st.subheader("Ask anything about your pipelines")

    # Quick question buttons
    st.write("**Quick questions:**")
    q_col1, q_col2, q_col3 = st.columns(3)
    if "question_input" not in st.session_state:
        st.session_state.question_input = ""

    q_col1, q_col2, q_col3 = st.columns(3)
    if q_col1.button("Which pipelines failed?"):
        st.session_state.question_input = "which pipelines failed?"
    if q_col2.button("Any database errors?"):
        st.session_state.question_input = "show me database connection errors"
    if q_col3.button("Overall health summary"):
        st.session_state.question_input = "give me an overall health summary of all pipelines"

    question = st.text_input("Or type your own question:",
                              value=st.session_state.question_input,
                              placeholder="e.g. which pipeline had the most timeouts?")

    # Detect intent for smarter filtering
    def get_status_filter(q):
        q = q.lower()
        if any(w in q for w in ["fail", "error", "broke", "down", "crash"]):
            return "failed"
        elif any(w in q for w in ["warn", "warning"]):
            return "warning"
        elif any(w in q for w in ["success", "passed", "completed"]):
            return "success"
        return None

    if st.button("🔍 Analyze", type="primary") and question:
        with st.spinner("Searching logs and generating summary..."):
            status_filter = get_status_filter(question)

            # Smart filtering: use metadata filter if status detected
            if status_filter:
                results = collection.query(
                    query_texts=[question],
                    n_results=8,
                    where={"status": status_filter}
                )
            else:
                results = collection.query(
                    query_texts=[question],
                    n_results=8
                )

            logs_text = "\n".join(results["documents"][0])

            response = client_ai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": """You are a senior data engineer reviewing ETL pipeline logs. 
                    When answering:
                    - Be specific about which pipelines are affected
                    - Mention exact error types
                    - Suggest possible root causes
                    - Keep it concise and actionable"""},
                    {"role": "user", "content": f"Question: {question}\n\nRelevant logs:\n{logs_text}\n\nProvide a clear, actionable summary."}
                ]
            )
            summary = response.choices[0].message.content

        st.subheader("🤖 AI Summary")
        st.success(summary)

        st.subheader("📋 Relevant Logs Found")
        for i, doc in enumerate(results["documents"][0]):
            if "FAILED" in doc:
                st.error(f"🔴 {doc}")
            elif "WARNING" in doc:
                st.warning(f"🟡 {doc}")
            else:
                st.info(f"🟢 {doc}")

# ===================== TAB 2: PIPELINE HEALTH =====================
with tab2:
    st.subheader("Pipeline-by-Pipeline Breakdown")

    for pipeline, stats in pipeline_stats.items():
        total_runs = stats["success"] + stats["failed"] + stats["warning"]
        success_rate = round(stats["success"] / total_runs * 100) if total_runs > 0 else 0

        with st.expander(f"{'🟢' if success_rate > 70 else '🔴'} {pipeline} — {success_rate}% success rate"):
            c1, c2, c3 = st.columns(3)
            c1.metric("✅ Success", stats["success"])
            c2.metric("❌ Failed", stats["failed"])
            c3.metric("⚠️ Warning", stats["warning"])

            st.progress(success_rate / 100)

            if stats["errors"]:
                st.write("**Most common errors:**")
                error_counts = defaultdict(int)
                for e in stats["errors"]:
                    error_counts[e] += 1
                for error, count in sorted(error_counts.items(), key=lambda x: -x[1]):
                    st.code(f"{count}x — {error}")

# ===================== TAB 3: ANOMALIES =====================
with tab3:
    st.subheader("🚨 Automatically Detected Anomalies")

    anomalies = []

    # High failure rate pipelines
    for pipeline, stats in pipeline_stats.items():
        total_runs = stats["success"] + stats["failed"] + stats["warning"]
        failure_rate = stats["failed"] / total_runs if total_runs > 0 else 0
        if failure_rate > 0.4:
            anomalies.append({
                "severity": "🔴 HIGH",
                "pipeline": pipeline,
                "issue": f"High failure rate: {round(failure_rate*100)}% of runs failed",
                "recommendation": "Investigate root cause immediately. Check source data availability and database connectivity."
            })
        elif failure_rate > 0.2:
            anomalies.append({
                "severity": "🟡 MEDIUM",
                "pipeline": pipeline,
                "issue": f"Elevated failure rate: {round(failure_rate*100)}% of runs failed",
                "recommendation": "Monitor closely and review error logs for patterns."
            })

    # Repeated same error
    for pipeline, stats in pipeline_stats.items():
        if stats["errors"]:
            error_counts = defaultdict(int)
            for e in stats["errors"]:
                error_counts[e] += 1
            for error, count in error_counts.items():
                if count >= 3:
                    anomalies.append({
                        "severity": "🟡 MEDIUM",
                        "pipeline": pipeline,
                        "issue": f"Repeated error ({count}x): {error}",
                        "recommendation": "This error is recurring — likely a systemic issue, not a one-off."
                    })

    if anomalies:
        # Ask AI to summarize all anomalies
        if st.button("🤖 Generate AI Anomaly Report"):
            with st.spinner("Analyzing anomalies..."):
                anomaly_text = "\n".join([f"{a['severity']} - {a['pipeline']}: {a['issue']}" for a in anomalies])
                response = client_ai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a data reliability engineer. Analyze these pipeline anomalies and provide a prioritized action plan."},
                        {"role": "user", "content": f"Anomalies detected:\n{anomaly_text}\n\nProvide a prioritized action plan to fix these issues."}
                    ]
                )
            st.success(response.choices[0].message.content)
            st.divider()

        for anomaly in anomalies:
            if "HIGH" in anomaly["severity"]:
                st.error(f"**{anomaly['severity']}** | `{anomaly['pipeline']}`\n\n{anomaly['issue']}\n\n💡 *{anomaly['recommendation']}*")
            else:
                st.warning(f"**{anomaly['severity']}** | `{anomaly['pipeline']}`\n\n{anomaly['issue']}\n\n💡 *{anomaly['recommendation']}*")
    else:
        st.success("✅ No anomalies detected! All pipelines are healthy.")