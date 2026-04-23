import streamlit as st
import chromadb
from chromadb.utils import embedding_functions
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from collections import defaultdict
from datetime import datetime

load_dotenv()
client_ai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
client_db = chromadb.PersistentClient(path="./chroma_db")
ef = embedding_functions.DefaultEmbeddingFunction()
collection = client_db.get_or_create_collection(
    name="pipeline_logs",
    embedding_function=ef
)

def load_logs(uploaded_file=None):
    if uploaded_file:
        return json.load(uploaded_file)
    with open("logs.json", "r") as f:
        return json.load(f)

# --- Page Config ---
st.set_page_config(page_title="Pipeline Observability", page_icon="🔭", layout="wide")

# --- Custom CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    .main { background-color: #0a0e1a; }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1117 0%, #161b27 100%);
        border-right: 1px solid #21262d;
    }
    
    [data-testid="stSidebar"] * {
        color: #c9d1d9 !important;
    }
    
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label {
        color: #c9d1d9 !important;
    }
    
    .section-header {
        color: #ffffff !important;
    }
    
    p, span, li {
        color: #c9d1d9 !important;
    }
    
    .stChatMessage p {
        color: #f0f6fc !important;
        font-size: 0.95rem !important;
    }
    
    .stMarkdown p {
        color: #c9d1d9 !important;
    }
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #ffffff !important;
    }
    
    [data-testid="stChatInput"] {
        color: #ffffff !important;
    }
    
    .stCaption {
        color: #c9d1d9 !important;
    }
    
    small, .small {
        color: #c9d1d9 !important;
    }
    
    [data-testid="stText"] {
        color: #c9d1d9 !important;
    }
    
    .hero-title {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #58a6ff, #bc8cff, #ff7b7b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    
    .hero-subtitle {
        color: #8b949e;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #161b27, #1c2333);
        border: 1px solid #21262d;
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        transition: transform 0.2s;
    }
    
    .metric-card:hover { transform: translateY(-2px); }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #f0f6fc;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .status-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .badge-success { background: #1a3a2a; color: #3fb950; border: 1px solid #3fb950; }
    .badge-failed { background: #3a1a1a; color: #f85149; border: 1px solid #f85149; }
    .badge-warning { background: #3a2e1a; color: #d29922; border: 1px solid #d29922; }
    
    .log-card {
        background: #161b27;
        border-radius: 10px;
        padding: 14px 18px;
        margin: 8px 0;
        border-left: 4px solid #21262d;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
    }
    
    .log-failed { border-left-color: #f85149; background: #2d1515; color: #ffb3b3 !important; }
    .log-warning { border-left-color: #d29922; background: #2d2510; color: #ffd980 !important; }
    .log-success { border-left-color: #3fb950; background: #152d1e; color: #a3f0b5 !important; }
    
    .log-card {
        color: #e6edf3 !important;
    }
    
    .section-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #ffffff !important;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #21262d;
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
    
    }
    
    .stTabs [data-baseweb="tab-list"] {
        background: #161b27;
        border-radius: 10px;
        padding: 4px;
        gap: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #8b949e;
        font-weight: 500;
        padding: 8px 20px;
    }
    
    .stTabs [aria-selected="true"] {
        background: #21262d !important;
        color: #f0f6fc !important;
    }
    
    div[data-testid="stMetric"] {
        background: #161b27;
        border: 1px solid #21262d;
        border-radius: 12px;
        padding: 16px;
    }
    
    div[data-testid="stMetric"] label {
        color: #c9d1d9 !important;
        font-size: 0.9rem !important;
    }
    
    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    
    div[data-testid="stMetricDelta"] {
        color: #8b949e !important;
    
    }
    
    .stButton button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    .stTextInput input {
        background: #161b27 !important;
        border: 1px solid #21262d !important;
        border-radius: 8px !important;
        color: #f0f6fc !important;
    }

    .stChatMessage {
        background: #161b27 !important;
        border-radius: 12px !important;
        border: 1px solid #21262d !important;
    }
    
    .anomaly-high {
        background: linear-gradient(135deg, #2d0f0f, #1a0808);
        border: 1px solid #f85149;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
    }
    
    .anomaly-medium {
        background: linear-gradient(135deg, #2d1f0f, #1a1208);
        border: 1px solid #d29922;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.markdown("### ⚙️ Controls")
    st.divider()

    st.markdown("**📁 Upload Log File**")
    uploaded_file = st.file_uploader("Upload JSON logs", type=["json"], label_visibility="collapsed")
    if uploaded_file:
        st.success("✅ Custom logs loaded!")

    st.divider()

    logs = load_logs(uploaded_file)
    dates = [datetime.strptime(l["timestamp"], "%Y-%m-%d %H:%M:%S") for l in logs]
    min_date = min(dates).date()
    max_date = max(dates).date()

    st.markdown("**📅 Date Range**")
    date_range = st.date_input("", value=(min_date, max_date),
                                min_value=min_date, max_value=max_date,
                                label_visibility="collapsed")

    st.divider()
    st.markdown("**🔢 Results per Query**")
    n_results = st.slider("", 3, 15, 8, label_visibility="collapsed")

    st.divider()
    st.markdown("**📌 Quick Stats**")
    total_pipelines = len(set(l["pipeline"] for l in logs))
    st.markdown(f"- **{total_pipelines}** unique pipelines")
    st.markdown(f"- **{len(logs)}** total log entries")
    error_types = len(set(l["error"] for l in logs if l["error"]))
    st.markdown(f"- **{error_types}** distinct error types")

# --- Filter logs by date ---
if len(date_range) == 2:
    start_date, end_date = date_range
    logs = [l for l in logs if start_date <= datetime.strptime(l["timestamp"], "%Y-%m-%d %H:%M:%S").date() <= end_date]

# --- Stats ---
total = len(logs)
failed = [l for l in logs if l["status"] == "failed"]
success = [l for l in logs if l["status"] == "success"]
warning = [l for l in logs if l["status"] == "warning"]
pipeline_stats = defaultdict(lambda: {"success": 0, "failed": 0, "warning": 0, "errors": []})
for l in logs:
    pipeline_stats[l["pipeline"]][l["status"]] += 1
    if l["error"]:
        pipeline_stats[l["pipeline"]]["errors"].append(l["error"])

# --- Header ---
st.markdown('<div class="hero-title">🔭 Pipeline Observability</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">LLM-powered ETL log analysis · Anomaly detection · Natural language querying</div>', unsafe_allow_html=True)

# --- Health indicator ---
health_score = round(len(success) / total * 100) if total else 0
if health_score >= 80:
    health_color = "#3fb950"
    health_label = "Healthy"
elif health_score >= 60:
    health_color = "#d29922"
    health_label = "Degraded"
else:
    health_color = "#f85149"
    health_label = "Critical"

st.markdown(f"""
<div style="background: linear-gradient(135deg, #161b27, #1c2333); border: 1px solid #21262d; 
     border-radius: 16px; padding: 16px 24px; margin-bottom: 24px; display: flex; align-items: center; gap: 16px;">
    <div style="width: 14px; height: 14px; border-radius: 50%; background: {health_color}; 
         box-shadow: 0 0 10px {health_color};"></div>
    <div>
        <span style="color: {health_color}; font-weight: 700; font-size: 1.1rem;">System {health_label}</span>
        <span style="color: #8b949e; margin-left: 12px; font-size: 0.9rem;">{health_score}% success rate across all pipelines</span>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Metrics ---
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Runs", total)
col2.metric("✅ Success", len(success), f"{round(len(success)/total*100)}%" if total else "0%")
col3.metric("❌ Failed", len(failed), f"-{round(len(failed)/total*100)}%" if total else "0%", delta_color="inverse")
col4.metric("⚠️ Warning", len(warning))
col5.metric("🏥 Health Score", f"{health_score}%")

st.divider()

# --- Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔍 Ask AI", "💬 Chat", "📊 Pipeline Health", "📈 Trends", "🚨 Anomalies"])

# ===================== TAB 1: ASK AI =====================
with tab1:
    st.markdown("### 🔍 Ask anything about your pipelines")

    if "question_input" not in st.session_state:
        st.session_state.question_input = ""

    q_col1, q_col2, q_col3, q_col4 = st.columns(4)
    if q_col1.button("🔴 Which failed?"):
        st.session_state.question_input = "which pipelines failed?"
    if q_col2.button("🔌 DB errors?"):
        st.session_state.question_input = "show me database connection errors"
    if q_col3.button("📋 Health summary"):
        st.session_state.question_input = "give me an overall health summary of all pipelines"
    if q_col4.button("⏱️ Timeouts?"):
        st.session_state.question_input = "show me timeout errors"

    question = st.text_input("", value=st.session_state.question_input,
                              placeholder="e.g. which pipeline had the most timeouts?",
                              label_visibility="collapsed")

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
        with st.spinner("🤖 Analyzing your pipeline logs..."):
            status_filter = get_status_filter(question)
            if status_filter:
                results = collection.query(query_texts=[question], n_results=n_results,
                                           where={"status": status_filter})
            else:
                results = collection.query(query_texts=[question], n_results=n_results)

            logs_text = "\n".join(results["documents"][0])
            response = client_ai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": """You are a senior data engineer reviewing ETL pipeline logs. 
                    Be specific about pipelines, error types, and suggest root causes. Keep it concise and actionable."""},
                    {"role": "user", "content": f"Question: {question}\n\nLogs:\n{logs_text}\n\nProvide a clear, actionable summary."}
                ]
            )
            summary = response.choices[0].message.content

        st.markdown("### 🤖 AI Summary")
        st.success(summary)

        col_a, col_b = st.columns([1, 4])
        with col_a:
            st.download_button("📥 Download", 
                data=f"Q: {question}\n\nSummary:\n{summary}\n\nLogs:\n{logs_text}",
                file_name="pipeline_summary.txt", mime="text/plain")

        st.markdown("### 📋 Relevant Logs")
        for doc in results["documents"][0]:
            if "FAILED" in doc:
                st.markdown(f'<div class="log-card log-failed">🔴 {doc}</div>', unsafe_allow_html=True)
            elif "WARNING" in doc:
                st.markdown(f'<div class="log-card log-warning">🟡 {doc}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="log-card log-success">🟢 {doc}</div>', unsafe_allow_html=True)

# ===================== TAB 2: CHAT =====================
with tab2:
    st.markdown("### 💬 Chat with your pipeline logs")
    st.caption("Ask follow-up questions naturally — the AI remembers context")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    chat_input = st.chat_input("Ask about your pipelines...")
    if chat_input:
        st.session_state.chat_history.append({"role": "user", "content": chat_input})
        with st.chat_message("user"):
            st.write(chat_input)

        with st.spinner("Thinking..."):
            all_logs_text = ""
            for status in ["failed", "warning", "success"]:
                results = collection.query(query_texts=[chat_input], n_results=3,
                                           where={"status": status})
                if results["documents"][0]:
                    all_logs_text += f"\n{status.upper()} LOGS:\n"
                    all_logs_text += "\n".join(results["documents"][0])

            messages = [{"role": "system", "content": """You are a helpful data engineering assistant analyzing ETL pipeline logs. 
                The logs contain entries with statuses: success, failed, and warning.
                Always look carefully at ALL logs provided including failed ones.
                Be specific about pipeline names, error types, and timestamps when answering."""}]
            for h in st.session_state.chat_history[-6:]:
                messages.append(h)
            messages.append({"role": "user", "content": f"Context logs:\n{all_logs_text}\n\nQuestion: {chat_input}"})

            response = client_ai.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
            reply = response.choices[0].message.content

        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.write(reply)

    if st.button("🗑️ Clear chat"):
        st.session_state.chat_history = []
        st.rerun()

# ===================== TAB 3: PIPELINE HEALTH =====================
with tab3:
    st.markdown('<div class="section-header">Pipeline-by-Pipeline Breakdown</div>', unsafe_allow_html=True)

    for pipeline, stats in sorted(pipeline_stats.items()):
        total_runs = stats["success"] + stats["failed"] + stats["warning"]
        success_rate = round(stats["success"] / total_runs * 100) if total_runs > 0 else 0

        if success_rate >= 80:
            badge = "🟢"
            status_class = "badge-success"
        elif success_rate >= 50:
            badge = "🟡"
            status_class = "badge-warning"
        else:
            badge = "🔴"
            status_class = "badge-failed"

        with st.expander(f"{badge} {pipeline.upper()} — {success_rate}% success rate"):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("✅ Success", stats["success"])
            c2.metric("❌ Failed", stats["failed"])
            c3.metric("⚠️ Warning", stats["warning"])
            c4.metric("🏥 Health", f"{success_rate}%")

            st.progress(success_rate / 100)

            if stats["errors"]:
                st.markdown("**Most common errors:**")
                error_counts = defaultdict(int)
                for e in stats["errors"]:
                    error_counts[e] += 1
                for error, count in sorted(error_counts.items(), key=lambda x: -x[1]):
                    col_e1, col_e2 = st.columns([1, 6])
                    col_e1.markdown(f"**`{count}x`**")
                    col_e2.code(error)

# ===================== TAB 4: TRENDS =====================
with tab4:
    st.markdown('<div class="section-header">📈 Pipeline Failure Trends</div>', unsafe_allow_html=True)

    df = pd.DataFrame(logs)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["date"] = df["timestamp"].dt.date

    chart_bg = "#0d1117"
    chart_font = "#c9d1d9"

    daily = df.groupby(["date", "status"]).size().reset_index(name="count")
    fig1 = px.bar(daily, x="date", y="count", color="status",
                  color_discrete_map={"success": "#3fb950", "failed": "#f85149", "warning": "#d29922"},
                  title="Daily Pipeline Runs by Status",
                  labels={"date": "Date", "count": "Runs"}, barmode="stack")
    fig1.update_layout(plot_bgcolor=chart_bg, paper_bgcolor=chart_bg,
                       font_color=chart_font, legend_bgcolor=chart_bg,
                       title_font_size=16, margin=dict(t=50, b=40))
    fig1.update_xaxes(gridcolor="#21262d", showgrid=True)
    fig1.update_yaxes(gridcolor="#21262d", showgrid=True)
    st.plotly_chart(fig1, use_container_width=True)

    pipeline_df = pd.DataFrame([
        {"pipeline": p, "failure_rate": round(s["failed"] / (s["success"] + s["failed"] + s["warning"]) * 100, 1),
         "success": s["success"], "failed": s["failed"]}
        for p, s in pipeline_stats.items()
    ]).sort_values("failure_rate", ascending=True)

    fig2 = go.Figure(go.Bar(
        x=pipeline_df["failure_rate"], y=pipeline_df["pipeline"],
        orientation='h',
        marker=dict(
            color=pipeline_df["failure_rate"],
            colorscale=[[0, "#3fb950"], [0.5, "#d29922"], [1, "#f85149"]],
            showscale=True,
            colorbar=dict(title="Failure %", tickfont=dict(color=chart_font))
        ),
        text=pipeline_df["failure_rate"].apply(lambda x: f"{x}%"),
        textposition="outside", textfont=dict(color=chart_font)
    ))
    fig2.update_layout(title="Failure Rate by Pipeline", plot_bgcolor=chart_bg,
                       paper_bgcolor=chart_bg, font_color=chart_font,
                       xaxis=dict(gridcolor="#21262d", title="Failure Rate (%)"),
                       yaxis=dict(gridcolor="#21262d"), margin=dict(t=50, b=40))
    st.plotly_chart(fig2, use_container_width=True)

    error_logs = [l for l in logs if l["error"]]
    if error_logs:
        error_df = pd.DataFrame(error_logs)
        error_counts = error_df["error"].value_counts().reset_index()
        error_counts.columns = ["error", "count"]
        error_counts["short"] = error_counts["error"].apply(lambda x: x.split(":")[0])
        fig3 = px.pie(error_counts, names="short", values="count",
                      title="Error Type Distribution",
                      color_discrete_sequence=["#f85149", "#d29922", "#58a6ff", "#3fb950", "#bc8cff"],
                      hole=0.4)
        fig3.update_layout(paper_bgcolor=chart_bg, font_color=chart_font,
                           legend_bgcolor=chart_bg, title_font_size=16)
        fig3.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig3, use_container_width=True)

# ===================== TAB 5: ANOMALIES =====================
with tab5:
    st.markdown('<div class="section-header">🚨 Automatically Detected Anomalies</div>', unsafe_allow_html=True)

    anomalies = []
    for pipeline, stats in pipeline_stats.items():
        total_runs = stats["success"] + stats["failed"] + stats["warning"]
        failure_rate = stats["failed"] / total_runs if total_runs > 0 else 0
        if failure_rate > 0.4:
            anomalies.append({"severity": "HIGH", "pipeline": pipeline,
                               "issue": f"High failure rate: {round(failure_rate*100)}% of runs failed",
                               "recommendation": "Investigate immediately. Check source data and DB connectivity."})
        elif failure_rate > 0.2:
            anomalies.append({"severity": "MEDIUM", "pipeline": pipeline,
                               "issue": f"Elevated failure rate: {round(failure_rate*100)}% of runs failed",
                               "recommendation": "Monitor closely and review error patterns."})

    for pipeline, stats in pipeline_stats.items():
        if stats["errors"]:
            error_counts = defaultdict(int)
            for e in stats["errors"]:
                error_counts[e] += 1
            for error, count in error_counts.items():
                if count >= 3:
                    anomalies.append({"severity": "MEDIUM", "pipeline": pipeline,
                                       "issue": f"Repeated error ({count}x): {error}",
                                       "recommendation": "Recurring error — likely systemic, not a one-off."})

    if anomalies:
        high = [a for a in anomalies if a["severity"] == "HIGH"]
        medium = [a for a in anomalies if a["severity"] == "MEDIUM"]

        col_h, col_m = st.columns(2)
        col_h.markdown(f"### 🔴 High Severity ({len(high)})")
        col_m.markdown(f"### 🟡 Medium Severity ({len(medium)})")

        if st.button("🤖 Generate AI Action Plan", type="primary"):
            with st.spinner("Generating prioritized action plan..."):
                anomaly_text = "\n".join([f"{a['severity']} - {a['pipeline']}: {a['issue']}" for a in anomalies])
                response = client_ai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a data reliability engineer. Give a prioritized, numbered action plan to fix these pipeline anomalies."},
                        {"role": "user", "content": f"Anomalies:\n{anomaly_text}\n\nGive a prioritized action plan."}
                    ]
                )
                report = response.choices[0].message.content
            st.success(report)
            st.download_button("📥 Download Report", data=report,
                               file_name="anomaly_report.txt", mime="text/plain")
            st.divider()

        for anomaly in anomalies:
            if anomaly["severity"] == "HIGH":
                st.markdown(f"""
                <div class="anomaly-high">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="color:#f85149; font-weight:700; font-size:1rem;">🔴 HIGH SEVERITY</span>
                        <code style="background:#2d0f0f; color:#f85149; padding:2px 8px; border-radius:4px;">{anomaly['pipeline']}</code>
                    </div>
                    <p style="color:#f0f6fc; margin:10px 0 6px 0;">{anomaly['issue']}</p>
                    <p style="color:#8b949e; font-size:0.85rem;">💡 {anomaly['recommendation']}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="anomaly-medium">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="color:#d29922; font-weight:700; font-size:1rem;">🟡 MEDIUM SEVERITY</span>
                        <code style="background:#2d1f0f; color:#d29922; padding:2px 8px; border-radius:4px;">{anomaly['pipeline']}</code>
                    </div>
                    <p style="color:#f0f6fc; margin:10px 0 6px 0;">{anomaly['issue']}</p>
                    <p style="color:#8b949e; font-size:0.85rem;">💡 {anomaly['recommendation']}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.success("✅ No anomalies detected! All pipelines are healthy.")