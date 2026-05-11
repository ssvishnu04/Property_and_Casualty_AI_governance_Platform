"""
streamlit_app.py

Purpose:
Enterprise AI Governance Dashboard
for Insurance & Reinsurance — P&C Domain.
"""

import os
import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import requests
import pandas as pd
import streamlit as st
import plotly.express as px

from api.models.governance_models import GovernanceEvaluationRequest
from api.services.guardrail_service import evaluate_governance_request
from api.services.agent_response_service import generate_agent_response
from api.services.event_service import load_events, save_event
from api.services.agent_service import get_agent_by_id

try:
    from api.services.agent_service import get_agents
except ImportError:
    get_agents = None

try:
    from api.services.tool_service import get_tools
except ImportError:
    get_tools = None


# -------------------------------------------------------------------
# Page Configuration
# -------------------------------------------------------------------

st.set_page_config(
    page_title="Insurance AI Control Tower",
    layout="wide",
)


# -------------------------------------------------------------------
# API Configuration
# -------------------------------------------------------------------

API_BASE_URL = "http://127.0.0.1:8000"

# Streamlit Cloud friendly mode.
# True = Streamlit runs without a separate FastAPI server.
# False = Streamlit calls local FastAPI at API_BASE_URL.
DEMO_MODE = True

if "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]


# -------------------------------------------------------------------
# Helper Functions
# -------------------------------------------------------------------

@st.cache_data(ttl=30)
def fetch_data(endpoint: str):
    """
    Fetches data either from FastAPI or directly from local services
    for Streamlit Cloud demo mode.
    """

    if DEMO_MODE:

        if endpoint == "/agents/":
            if get_agents is not None:
                return get_agents()

            return load_json_from_possible_paths(
                [
                    "data/agents.json",
                    "data/registry/agents.json",
                    "data/governance/agents.json",
                    "agents.json",
                ]
            )

        if endpoint == "/tools/":
            if get_tools is not None:
                return get_tools()

            return load_json_from_possible_paths(
                [
                    "data/tools.json",
                    "data/registry/tools.json",
                    "data/governance/tools.json",
                    "tools.json",
                ]
            )

        if endpoint.startswith("/events/recent"):
            events = load_events()
            return list(reversed(events))[:1000]

        if endpoint == "/events/blocked":
            events = load_events()
            return [
                event
                for event in events
                if event.get("decision") == "Blocked"
            ]

        if endpoint == "/metrics/summary":
            events = load_events()

            total = len(events)

            allowed = len(
                [
                    event
                    for event in events
                    if event.get("decision") == "Allowed"
                ]
            )

            review = len(
                [
                    event
                    for event in events
                    if event.get("decision") == "Allowed with Review"
                ]
            )

            blocked = len(
                [
                    event
                    for event in events
                    if event.get("decision") == "Blocked"
                ]
            )

            return {
                "total_requests": total,
                "allowed_requests": allowed,
                "review_requests": review,
                "blocked_requests": blocked,
            }

        return {}

    response = requests.get(f"{API_BASE_URL}{endpoint}")
    response.raise_for_status()
    return response.json()


def post_data(endpoint: str, payload: dict):
    """
    Posts data either to FastAPI or directly executes governance workflow
    for Streamlit Cloud demo mode.
    """

    if DEMO_MODE and endpoint == "/governance/evaluate":

        request = GovernanceEvaluationRequest(
            user_id=payload["user_id"],
            agent_id=payload["agent_id"],
            tool_name=payload["tool_name"],
            prompt=payload["prompt"],
        )

        result = evaluate_governance_request(
            request
        )

        agent = get_agent_by_id(
            request.agent_id
        )

        agent_name = (
            agent.get("agent_name", request.agent_id)
            if agent
            else request.agent_id
        )

        rag_metadata = {}

        if result.decision == "Blocked":

            agent_response_text = (
                "No AI response generated because the request was blocked "
                "by enterprise governance controls."
            )

        else:

            agent_result = generate_agent_response(
                agent_id=request.agent_id,
                prompt=request.prompt,
            )

            agent_response_text = agent_result.get(
                "response",
                "No agent response generated.",
            )

            rag_metadata = agent_result.get(
                "rag_metadata",
                {},
            )

        result.agent_response = agent_response_text

        existing_events = load_events()
        next_event_number = len(existing_events) + 1
        now = pd.Timestamp.now().isoformat()

        new_event = {
            "request_id": f"REQ-{next_event_number:07d}",
            "user_id": result.user_id,
            "agent_id": result.agent_id,
            "agent_name": agent_name,
            "tool_used": result.tool_name,
            "prompt": result.prompt,
            "decision": result.decision,
            "risk_score": result.risk_score,
            "risk_level": result.risk_level,
            "hallucination_risk_score": 0.10
            if result.decision == "Allowed"
            else 0.75,
            "latency_ms": 500,
            "tokens_used": 250,
            "model_name": "enterprise-governance-agent",
            "triggered_rules": result.triggered_rules,
            "agent_response": agent_response_text,
            "rag_domain": rag_metadata.get("rag_domain"),
            "retrieved_chunk_count": rag_metadata.get(
                "retrieved_chunk_count",
                0,
            ),
            "retrieval_latency_seconds": rag_metadata.get(
                "retrieval_latency_seconds",
                0,
            ),
            "retrieved_sources": rag_metadata.get(
                "retrieved_sources",
                [],
            ),
            "event_timestamp": now,
            "response_timestamp": now,
            "source_system": "streamlit_demo_mode",
        }

        save_event(new_event)

        if hasattr(result, "model_dump"):
            return result.model_dump()

        return result.dict()

    response = requests.post(
        f"{API_BASE_URL}{endpoint}",
        json=payload,
    )
    response.raise_for_status()
    return response.json()


def safe_dataframe(records):
    if not records:
        return pd.DataFrame()
    return pd.DataFrame(records)


def convert_list_columns_to_text(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    for col in df.columns:
        df[col] = df[col].apply(
            lambda x: ", ".join(x) if isinstance(x, list) else x
        )

    return df


def add_risk_band(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    def classify(score):
        if score >= 0.75:
            return "High"
        if score >= 0.40:
            return "Medium"
        return "Low"

    if "risk_score" in df.columns:
        df["risk_band"] = df["risk_score"].apply(classify)

    return df


def add_event_date(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if not df.empty and "event_timestamp" in df.columns:
        df["event_date"] = pd.to_datetime(
            df["event_timestamp"],
            errors="coerce",
        ).dt.date

    return df


def apply_event_filters(
    df: pd.DataFrame,
    selected_agent: str,
    selected_decision: str,
    risk_range,
    search_text: str,
    selected_event_date,
) -> pd.DataFrame:

    filtered_df = df.copy()

    if filtered_df.empty:
        return filtered_df

    if selected_agent != "All":
        filtered_df = filtered_df[
            filtered_df["agent_id"] == selected_agent
        ]

    if selected_decision != "All":
        filtered_df = filtered_df[
            filtered_df["decision"] == selected_decision
        ]

    filtered_df = filtered_df[
        (filtered_df["risk_score"] >= risk_range[0])
        & (filtered_df["risk_score"] <= risk_range[1])
    ]

    if selected_event_date is not None and "event_date" in filtered_df.columns:
        filtered_df = filtered_df[
            filtered_df["event_date"] == selected_event_date
        ]

    if search_text:
        filtered_df = filtered_df[
            filtered_df["prompt"]
            .str.lower()
            .str.contains(search_text.lower(), na=False)
        ]

    return filtered_df


def download_button(df: pd.DataFrame, file_name: str, label: str):
    csv_data = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label=label,
        data=csv_data,
        file_name=file_name,
        mime="text/csv",
    )


def parse_approved_tools(value):
    """
    Converts approved_tools into a clean list.

    Handles both:
    - list format from JSON
    - comma-separated text after dataframe conversion
    """

    if isinstance(value, list):
        return value

    if isinstance(value, str):
        return [
            tool.strip()
            for tool in value.split(",")
            if tool.strip()
        ]

    return []



def load_json_from_possible_paths(paths: list[str]):
    """
    Loads JSON from the first available path.
    Used as a fallback for Streamlit Cloud demo mode.
    """

    for path in paths:
        file_path = Path(path)

        if file_path.exists():
            with open(
                file_path,
                "r",
                encoding="utf-8",
            ) as file:
                return json.load(file)

    return []


def load_latest_json_summary(pattern: str) -> dict:
    """
    Loads latest evaluation summary JSON.
    """

    evaluation_results_dir = Path(
        "evaluation/evaluation_results"
    )

    if not evaluation_results_dir.exists():
        return {}

    summary_files = sorted(
        evaluation_results_dir.glob(pattern),
        reverse=True,
    )

    if not summary_files:
        return {}

    with open(
        summary_files[0],
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)



# -------------------------------------------------------------------
# Load Data From APIs
# -------------------------------------------------------------------

try:
    metrics = fetch_data("/metrics/summary")
    agents = fetch_data("/agents/")
    tools = fetch_data("/tools/")
    events = fetch_data("/events/recent?limit=1000")
    blocked_events = fetch_data("/events/blocked")

except Exception as error:
    st.error(
        "Unable to load application data. "
        "If running locally, make sure required data files exist. "
        f"Error: {error}"
    )
    st.stop()


agents_df = safe_dataframe(agents)
tools_df = safe_dataframe(tools)
events_df = safe_dataframe(events)
blocked_df = safe_dataframe(blocked_events)

agents_df = convert_list_columns_to_text(agents_df)
tools_df = convert_list_columns_to_text(tools_df)

events_df = add_risk_band(events_df)
blocked_df = add_risk_band(blocked_df)

events_df = add_event_date(events_df)
blocked_df = add_event_date(blocked_df)


# -------------------------------------------------------------------
# Friendly Display Fields
# -------------------------------------------------------------------

agent_name_map = {}

if not agents_df.empty:
    for _, row in agents_df.iterrows():
        agent_name_map[row["agent_id"]] = row["agent_name"]

if not events_df.empty:
    events_df["agent_name"] = events_df["agent_id"].map(agent_name_map)
    events_df["agent_name"] = events_df["agent_name"].fillna(
        events_df["agent_id"]
    )

if not blocked_df.empty:
    blocked_df["agent_name"] = blocked_df["agent_id"].map(agent_name_map)
    blocked_df["agent_name"] = blocked_df["agent_name"].fillna(
        blocked_df["agent_id"]
    )

if not tools_df.empty:
    tools_df["tool_display_name"] = (
        tools_df["tool_name"]
        .str.replace("_", " ")
        .str.title()
    )


# -------------------------------------------------------------------
# Header
# -------------------------------------------------------------------

st.title("Enterprise Agentic AI Governance Platform")
st.subheader("Insurance & Reinsurance — P&C Domain")
st.caption(
    "Insurance AI Control Tower for managing, monitoring, evaluating, "
    "and governing enterprise AI applications."
)

st.markdown("---")


# -------------------------------------------------------------------
# Dashboard KPI Calculations
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# Dashboard KPI Calculations
# -------------------------------------------------------------------

if events_df.empty or "decision" not in events_df.columns:
    dashboard_total_requests = 0
    dashboard_allowed_requests = 0
    dashboard_allowed_review_requests = 0
    dashboard_blocked_requests = 0
    dashboard_avg_hallucination = 0

else:
    dashboard_total_requests = len(events_df)

    dashboard_allowed_requests = len(
        events_df[
            events_df["decision"] == "Allowed"
        ]
    )

    dashboard_allowed_review_requests = len(
        events_df[
            events_df["decision"] == "Allowed with Review"
        ]
    )

    dashboard_blocked_requests = len(
        events_df[
            events_df["decision"] == "Blocked"
        ]
    )

    if "hallucination_risk_score" in events_df.columns:
        dashboard_avg_hallucination = round(
            events_df["hallucination_risk_score"].mean(),
            2,
        )
    else:
        dashboard_avg_hallucination = 0


# -------------------------------------------------------------------
# Executive KPI Row
# -------------------------------------------------------------------

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Recent Runtime Events", dashboard_total_requests)

with col2:
    st.metric("Allowed", dashboard_allowed_requests)

with col3:
    st.metric("Review Required", dashboard_allowed_review_requests)

with col4:
    st.metric("Blocked", dashboard_blocked_requests)

with col5:
    st.metric("Avg Hallucination Risk", dashboard_avg_hallucination)

st.markdown("---")


# -------------------------------------------------------------------
# Navigation Tabs
# -------------------------------------------------------------------

tabs = st.tabs(
    [
        "Executive Overview",
        "AI Gateway Playground",
        "AI Agent Registry",
        "Tool Registry",
        "AI Runtime Events",
        "Blocked Events",
        "Governance Audit Report",
    ]
)


# ===================================================================
# TAB 1 — EXECUTIVE OVERVIEW
# ===================================================================

with tabs[0]:

    st.header("Executive Governance Overview")

    st.markdown(
        """
        Centralized view of AI platform usage, blocked requests, risk distribution,
        and runtime performance across insurance and reinsurance AI applications.
        """
    )

    st.markdown("---")

    if events_df.empty:
        st.info("No AI runtime events available.")

    else:

        high_risk_count = len(events_df[events_df["risk_score"] >= 0.75])
        blocked_count = len(events_df[events_df["decision"] == "Blocked"])
        active_agents = events_df["agent_id"].nunique()

        status_col1, status_col2, status_col3, status_col4 = st.columns(4)

        with status_col1:
            st.success(f"Platform Healthy\n\n{active_agents} agents monitored")

        with status_col2:
            st.warning(f"High-Risk Events\n\n{high_risk_count}")

        with status_col3:
            st.error(f"Blocked\n\n{blocked_count}")

        with status_col4:
            st.info(f"Active Agents\n\n{active_agents}")

        st.markdown("---")

        events_for_charts = events_df.copy()

        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.subheader("Allowed vs Blocked Requests")

            allowed_blocked_df = (
                events_for_charts["decision"]
                .value_counts()
                .reset_index()
            )

            allowed_blocked_df.columns = ["decision", "count"]

            decision_colors = {
                "Allowed": "#2E7D32",
                "Allowed with Review": "#F9A825",
                "Blocked": "#C62828",
            }

            fig_allowed_blocked = px.bar(
                allowed_blocked_df,
                x="decision",
                y="count",
                color="decision",
                color_discrete_map=decision_colors,
                text="count",
            )

            fig_allowed_blocked.update_layout(
                showlegend=False,
                height=380,
                xaxis_title="Decision",
                yaxis_title="Request Count",
                margin=dict(l=20, r=20, t=30, b=20),
            )

            fig_allowed_blocked.update_traces(textposition="outside")

            st.plotly_chart(
                fig_allowed_blocked,
                use_container_width=True,
            )

        with chart_col2:
            st.subheader("Requests by AI Agent")

            requests_by_agent = (
                events_for_charts["agent_name"]
                .value_counts()
                .reset_index()
            )

            requests_by_agent.columns = ["agent_name", "request_count"]

            fig_requests_agent = px.bar(
                requests_by_agent,
                x="request_count",
                y="agent_name",
                orientation="h",
                text="request_count",
            )

            fig_requests_agent.update_layout(
                height=380,
                xaxis_title="Request Count",
                yaxis_title="AI Agent",
                margin=dict(l=20, r=20, t=30, b=20),
            )

            fig_requests_agent.update_traces(textposition="outside")

            st.plotly_chart(
                fig_requests_agent,
                use_container_width=True,
            )

        st.markdown("---")

        chart_col3, chart_col4 = st.columns(2)

        with chart_col3:
            st.subheader("Risk Band Distribution")

            risk_order = ["Low", "Medium", "High"]

            risk_band_df = (
                events_for_charts["risk_band"]
                .value_counts()
                .reindex(risk_order, fill_value=0)
                .reset_index()
            )

            risk_band_df.columns = ["risk_band", "count"]

            risk_colors = {
                "Low": "#2E7D32",
                "Medium": "#F9A825",
                "High": "#C62828",
            }

            fig_risk_band = px.bar(
                risk_band_df,
                x="risk_band",
                y="count",
                color="risk_band",
                color_discrete_map=risk_colors,
                text="count",
            )

            fig_risk_band.update_layout(
                showlegend=False,
                height=380,
                xaxis_title="Risk Band",
                yaxis_title="Request Count",
                margin=dict(l=20, r=20, t=30, b=20),
            )

            fig_risk_band.update_traces(textposition="outside")

            st.plotly_chart(
                fig_risk_band,
                use_container_width=True,
            )

        with chart_col4:
            st.subheader("Average Latency by AI Agent")

            latency_by_agent = (
                events_for_charts.groupby("agent_name")["latency_ms"]
                .mean()
                .round(2)
                .reset_index()
            )

            latency_by_agent["latency_seconds"] = (
                latency_by_agent["latency_ms"] / 1000
            ).round(2)

            fig_latency = px.bar(
                latency_by_agent,
                x="latency_seconds",
                y="agent_name",
                orientation="h",
                text="latency_seconds",
            )

            fig_latency.update_layout(
                height=380,
                xaxis_title="Average Latency (seconds)",
                yaxis_title="AI Agent",
                margin=dict(l=20, r=20, t=30, b=20),
            )

            fig_latency.update_traces(
                texttemplate="%{text}s",
                textposition="outside",
            )

            st.plotly_chart(
                fig_latency,
                use_container_width=True,
            )

        st.markdown("---")

        st.subheader("Recent High-Risk AI Events")

        high_risk_events = events_for_charts[
            events_for_charts["risk_score"] >= 0.75
        ].copy()

        if high_risk_events.empty:
            st.success("No high-risk events found in the current event window.")

        else:
            high_risk_columns = [
                "request_id",
                "user_id",
                "agent_name",
                "agent_id",
                "tool_used",
                "prompt",
                "decision",
                "risk_score",
                "risk_band",
                "triggered_rules",
                "event_timestamp",
            ]

            available_high_risk_columns = [
                col for col in high_risk_columns
                if col in high_risk_events.columns
            ]

            st.dataframe(
                high_risk_events[available_high_risk_columns],
                use_container_width=True,
                hide_index=True,
            )


        # ==========================================================
        # Advanced Governance Analytics
        # ==========================================================

        st.markdown("---")

        st.header("Advanced Governance Analytics")

        # ==========================================================
        # AI Evaluation Metrics
        # ==========================================================

        st.markdown("---")

        st.header("AI Evaluation Metrics")

        rag_summary = load_latest_json_summary(
            "rag_summary_*.json"
        )

        governance_summary = load_latest_json_summary(
            "governance_summary_*.json"
        )

        if rag_summary and governance_summary:

            metric_col1, metric_col2, metric_col3, metric_col4 = (
                st.columns(4)
            )

            with metric_col1:

                st.metric(
                    "Faithfulness",
                    round(
                        rag_summary.get(
                            "average_faithfulness_score",
                            0,
                        ),
                        4,
                    ),
                )

                st.metric(
                    "Context Precision",
                    round(
                        rag_summary.get(
                            "average_context_precision_score",
                            0,
                        ),
                        4,
                    ),
                )

            with metric_col2:

                st.metric(
                    "Answer Relevancy",
                    round(
                        rag_summary.get(
                            "average_answer_relevancy_score",
                            0,
                        ),
                        4,
                    ),
                )

                st.metric(
                    "Context Recall",
                    round(
                        rag_summary.get(
                            "average_context_recall_score",
                            0,
                        ),
                        4,
                    ),
                )

            with metric_col3:

                st.metric(
                    "Governance Pass Rate",
                    round(
                        governance_summary.get(
                            "governance_pass_rate",
                            0,
                        ),
                        4,
                    ),
                )

                st.metric(
                    "Average Governance Risk",
                    round(
                        governance_summary.get(
                            "average_governance_risk_score",
                            0,
                        ),
                        4,
                    ),
                )

            with metric_col4:

                st.metric(
                    "Avg Retrieved Chunks",
                    round(
                        rag_summary.get(
                            "average_retrieved_chunk_count",
                            0,
                        ),
                        4,
                    ),
                )

                st.metric(
                    "Avg Retrieval Latency",
                    round(
                        rag_summary.get(
                            "average_retrieval_latency_seconds",
                            0,
                        ),
                        4,
                    ),
                )

        else:

            st.info(
                "No evaluation metrics available yet. "
                "Run evaluation/ragas_eval.py locally and commit the generated "
                "evaluation summary JSON files if you want them visible in Streamlit Cloud."
            )

        advanced_chart_col1, advanced_chart_col2 = st.columns(2)

        with advanced_chart_col1:

            st.subheader("RAG Domain Usage")

            if (
                not events_df.empty
                and "rag_domain" in events_df.columns
            ):

                rag_domain_df = (
                    events_df["rag_domain"]
                    .fillna("No RAG / Blocked")
                    .value_counts()
                    .reset_index()
                )

                rag_domain_df.columns = [
                    "rag_domain",
                    "request_count",
                ]

                fig_rag_domains = px.pie(
                    rag_domain_df,
                    names="rag_domain",
                    values="request_count",
                    hole=0.4,
                )

                fig_rag_domains.update_layout(
                    height=400,
                    margin=dict(l=20, r=20, t=30, b=20),
                )

                st.plotly_chart(
                    fig_rag_domains,
                    use_container_width=True,
                )

            else:
                st.info("No RAG domain data available.")

        with advanced_chart_col2:

            st.subheader("Average Retrieval Latency by Agent")

            if (
                not events_df.empty
                and "retrieval_latency_seconds"
                in events_df.columns
            ):

                retrieval_latency_df = events_df.copy()

                retrieval_latency_df["retrieval_latency_seconds"] = (
                    pd.to_numeric(
                        retrieval_latency_df["retrieval_latency_seconds"],
                        errors="coerce",
                    ).fillna(0)
                )

                retrieval_latency_df = (
                    retrieval_latency_df.groupby("agent_name")[
                        "retrieval_latency_seconds"
                    ]
                    .mean()
                    .round(3)
                    .reset_index()
                )

                fig_retrieval_latency = px.bar(
                    retrieval_latency_df,
                    x="retrieval_latency_seconds",
                    y="agent_name",
                    orientation="h",
                    text="retrieval_latency_seconds",
                )

                fig_retrieval_latency.update_layout(
                    xaxis_title="Average Retrieval Latency (seconds)",
                    yaxis_title="AI Agent",
                    height=400,
                    margin=dict(l=20, r=20, t=30, b=20),
                )

                fig_retrieval_latency.update_traces(
                    textposition="outside",
                )

                st.plotly_chart(
                    fig_retrieval_latency,
                    use_container_width=True,
                )

            else:
                st.info("No retrieval latency data available.")

        analytics_col3, analytics_col4 = st.columns(2)

        with analytics_col3:

            st.subheader("Average Retrieved Chunks by Agent")

            if (
                not events_df.empty
                and "retrieved_chunk_count"
                in events_df.columns
            ):

                chunk_df = events_df.copy()

                chunk_df["retrieved_chunk_count"] = (
                    pd.to_numeric(
                        chunk_df["retrieved_chunk_count"],
                        errors="coerce",
                    ).fillna(0)
                )

                chunk_df = (
                    chunk_df.groupby("agent_name")[
                        "retrieved_chunk_count"
                    ]
                    .mean()
                    .round(2)
                    .reset_index()
                )

                fig_chunks = px.bar(
                    chunk_df,
                    x="retrieved_chunk_count",
                    y="agent_name",
                    orientation="h",
                    text="retrieved_chunk_count",
                )

                fig_chunks.update_layout(
                    xaxis_title="Average Retrieved Chunks",
                    yaxis_title="AI Agent",
                    height=400,
                    margin=dict(l=20, r=20, t=30, b=20),
                )

                fig_chunks.update_traces(
                    textposition="outside",
                )

                st.plotly_chart(
                    fig_chunks,
                    use_container_width=True,
                )

            else:
                st.info("No retrieved chunk metrics available.")

        with analytics_col4:

            st.subheader("Hallucination Risk Trend")

            if (
                not events_df.empty
                and "hallucination_risk_score"
                in events_df.columns
                and "event_timestamp"
                in events_df.columns
            ):

                hallucination_df = events_df.copy()

                hallucination_df["event_timestamp"] = (
                    pd.to_datetime(
                        hallucination_df["event_timestamp"],
                        errors="coerce",
                    )
                )

                hallucination_df["hallucination_risk_score"] = (
                    pd.to_numeric(
                        hallucination_df["hallucination_risk_score"],
                        errors="coerce",
                    ).fillna(0)
                )

                hallucination_df = (
                    hallucination_df.dropna(
                        subset=["event_timestamp"]
                    )
                    .sort_values("event_timestamp")
                )

                if hallucination_df.empty:
                    st.info("No valid hallucination trend timestamps available.")

                else:
                    fig_hallucination = px.line(
                        hallucination_df,
                        x="event_timestamp",
                        y="hallucination_risk_score",
                        color="agent_name",
                        markers=True,
                    )

                    fig_hallucination.update_layout(
                        xaxis_title="Event Time",
                        yaxis_title="Hallucination Risk",
                        height=400,
                        margin=dict(l=20, r=20, t=30, b=20),
                    )

                    st.plotly_chart(
                        fig_hallucination,
                        use_container_width=True,
                    )

            else:
                st.info("No hallucination trend data available.")

        analytics_col5, analytics_col6 = st.columns(2)

        with analytics_col5:

            st.subheader("Decision Trend Over Time")

            if (
                not events_df.empty
                and "decision" in events_df.columns
                and "event_timestamp" in events_df.columns
            ):

                decision_trend_df = events_df.copy()

                decision_trend_df["event_timestamp"] = (
                    pd.to_datetime(
                        decision_trend_df["event_timestamp"],
                        errors="coerce",
                    )
                )

                decision_trend_df = decision_trend_df.dropna(
                    subset=["event_timestamp"]
                )

                if decision_trend_df.empty:
                    st.info("No valid decision trend timestamps available.")

                else:
                    decision_trend_df["event_hour"] = (
                        decision_trend_df["event_timestamp"]
                        .dt.floor("h")
                    )

                    decision_trend_df = (
                        decision_trend_df.groupby(
                            ["event_hour", "decision"]
                        )
                        .size()
                        .reset_index(name="request_count")
                    )

                    fig_decision_trend = px.line(
                        decision_trend_df,
                        x="event_hour",
                        y="request_count",
                        color="decision",
                        markers=True,
                    )

                    fig_decision_trend.update_layout(
                        xaxis_title="Event Time",
                        yaxis_title="Request Count",
                        height=400,
                        margin=dict(l=20, r=20, t=30, b=20),
                    )

                    st.plotly_chart(
                        fig_decision_trend,
                        use_container_width=True,
                    )

            else:
                st.info("No decision trend data available.")

        with analytics_col6:

            st.subheader("Average Governance Risk by Agent")

            if (
                not events_df.empty
                and "risk_score" in events_df.columns
            ):

                agent_risk_df = events_df.copy()

                agent_risk_df["risk_score"] = (
                    pd.to_numeric(
                        agent_risk_df["risk_score"],
                        errors="coerce",
                    ).fillna(0)
                )

                agent_risk_df = (
                    agent_risk_df.groupby("agent_name")[
                        "risk_score"
                    ]
                    .mean()
                    .round(3)
                    .reset_index()
                    .sort_values(
                        "risk_score",
                        ascending=False,
                    )
                )

                fig_agent_risk = px.bar(
                    agent_risk_df,
                    x="risk_score",
                    y="agent_name",
                    orientation="h",
                    text="risk_score",
                )

                fig_agent_risk.update_layout(
                    xaxis_title="Average Governance Risk Score",
                    yaxis_title="AI Agent",
                    height=400,
                    margin=dict(l=20, r=20, t=30, b=20),
                )

                fig_agent_risk.update_traces(
                    textposition="outside",
                )

                st.plotly_chart(
                    fig_agent_risk,
                    use_container_width=True,
                )

            else:
                st.info("No governance risk data available.")


# ===================================================================
# TAB 2 — AI GATEWAY PLAYGROUND
# ===================================================================

with tabs[1]:

    st.header("AI Gateway Playground")

    st.markdown(
        """
        Simulate enterprise AI governance evaluation.

        This playground evaluates:
        - Prompt injection
        - PII exposure
        - Unauthorized tool access
        - Sensitive data requests
        - Governance risk scoring
        """
    )

    st.markdown("---")

    agent_display_map = {
        row["agent_name"]: {
            "agent_id": row["agent_id"],
            "approved_tools": parse_approved_tools(row["approved_tools"]),
        }
        for _, row in agents_df.iterrows()
    }

    agent_options = list(agent_display_map.keys())

    if not agent_options:
        st.error("No AI agents were loaded. Please verify agents.json or agent service data.")
        st.stop()

    selected_agent_name = st.selectbox(
        "Select AI Agent",
        agent_options,
        key="cloud_agent_select",
    )

    if selected_agent_name not in agent_display_map:
        selected_agent_name = agent_options[0]

    selected_agent = agent_display_map[selected_agent_name]["agent_id"]

    approved_tools_for_agent = agent_display_map[selected_agent_name][
        "approved_tools"
    ]

    tool_display_map = {
        tool_name.replace("_", " ").title(): tool_name
        for tool_name in approved_tools_for_agent
    }

    if not tool_display_map:
        st.warning("No approved tools are configured for this agent.")
        selected_tool = None
    else:
        selected_tool_name = st.selectbox(
            "Select Approved Tool",
            list(tool_display_map.keys()),
        )

        selected_tool = tool_display_map[selected_tool_name]

    user_display_map = {
        "Claims Adjuster": "USR-00001",
        "Underwriting Analyst": "USR-00002",
        "Reinsurance Manager": "USR-00003",
        "Governance Auditor": "USR-00004",
    }

    selected_user_name = st.selectbox(
        "Select User Role",
        list(user_display_map.keys()),
    )

    selected_user = user_display_map[selected_user_name]

    prompt_input = st.text_area(
        "Enter Prompt",
        height=150,
        placeholder=(
            "Example:\n"
            "Summarize this underwriting submission."
        ),
    )

    if st.button("Evaluate Governance Risk"):

        if selected_tool is None:
            st.warning("Please configure or select an approved tool.")

        elif not prompt_input.strip():
            st.warning("Please enter a prompt.")

        else:
            payload = {
                "user_id": selected_user,
                "agent_id": selected_agent,
                "tool_name": selected_tool,
                "prompt": prompt_input,
            }

            try:
                result = post_data(
                    "/governance/evaluate",
                    payload,
                )

                st.cache_data.clear()

                st.markdown("---")

                decision = result["decision"]

                if decision == "Blocked":
                    st.error(f"Decision: {decision}")

                elif decision == "Allowed with Review":
                    st.warning(f"Decision: {decision}")

                else:
                    st.success(f"Decision: {decision}")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Risk Score", result["risk_score"])

                with col2:
                    st.metric("Risk Level", result["risk_level"])

                with col3:
                    st.metric(
                        "Triggered Rules",
                        len(result["triggered_rules"]),
                    )

                st.markdown("---")

                st.subheader("Triggered Governance Rules")

                rules = result["triggered_rules"]

                if rules:
                    for rule in rules:
                        st.write(f"- {rule}")
                else:
                    st.write("No governance violations detected.")

                st.subheader("Governance Explanation")
                st.info(result["explanation"])

                st.subheader("Governed AI Agent Response")
                st.write(
                    result.get(
                        "agent_response",
                        "No agent response returned.",
                    )
                )

                # ----------------------------------------------------------
                # RAG Transparency / Explainability
                # ----------------------------------------------------------

                runtime_events = fetch_data("/events/recent?limit=1")

                if runtime_events:

                    latest_event = runtime_events[0]

                    rag_domain = latest_event.get("rag_domain")

                    retrieved_chunk_count = latest_event.get(
                        "retrieved_chunk_count",
                        0,
                    )

                    retrieval_latency_seconds = latest_event.get(
                        "retrieval_latency_seconds",
                        0,
                    )

                    retrieved_sources = latest_event.get(
                        "retrieved_sources",
                        [],
                    )

                    if rag_domain:

                        st.markdown("---")

                        st.subheader(
                            "RAG Explainability & Retrieval Transparency"
                        )

                        rag_col1, rag_col2, rag_col3 = st.columns(3)

                        with rag_col1:
                            st.metric(
                                "RAG Domain",
                                str(rag_domain).upper(),
                            )

                        with rag_col2:
                            st.metric(
                                "Retrieved Chunks",
                                retrieved_chunk_count,
                            )

                        with rag_col3:
                            st.metric(
                                "Retrieval Latency",
                                f"{float(retrieval_latency_seconds):.2f}s",
                            )

                        if retrieved_sources:

                            st.markdown("### Retrieved Sources")

                            for idx, source in enumerate(
                                retrieved_sources,
                                start=1,
                            ):

                                source_name = source.get(
                                    "source",
                                    "Unknown Source",
                                )

                                with st.expander(
                                    f"Source {idx}: {source_name}"
                                ):

                                    st.write(
                                        f"**Domain:** "
                                        f"{source.get('domain', 'unknown')}"
                                    )

                                    st.write(
                                        f"**File Type:** "
                                        f"{source.get('file_type', 'unknown')}"
                                    )

                                    st.write(
                                        f"**Chunk Number:** "
                                        f"{source.get('chunk_number', 'unknown')}"
                                    )

                                    st.write(
                                        f"**Similarity Score:** "
                                        f"{source.get('similarity_score', 'N/A')}"
                                    )

                        else:
                            st.info(
                                "No retrieved source metadata was available "
                                "for this response."
                            )

                st.info(
                    "This request has been evaluated. Refresh or switch tabs "
                    "to see the latest event in AI Runtime Events."
                )

            except Exception as error:
                st.error(f"Error during evaluation: {error}")


# ===================================================================
# TAB 3 — AI AGENT REGISTRY
# ===================================================================

with tabs[2]:

    st.header("AI Agent Registry")

    st.markdown(
        "Registered enterprise AI applications onboarded into the "
        "Insurance AI Control Tower."
    )

    if agents_df.empty:
        st.info("No agents available.")

    else:
        filter_col1, filter_col2, filter_col3 = st.columns(3)

        with filter_col1:
            business_units = ["All"] + sorted(
                agents_df["business_unit"].dropna().unique().tolist()
            )

            selected_business_unit = st.selectbox(
                "Filter by Business Unit",
                business_units,
            )

        with filter_col2:
            risk_tiers = ["All"] + sorted(
                agents_df["risk_tier"].dropna().unique().tolist()
            )

            selected_risk_tier = st.selectbox(
                "Filter by Risk Tier",
                risk_tiers,
            )

        with filter_col3:
            statuses = ["All"] + sorted(
                agents_df["status"].dropna().unique().tolist()
            )

            selected_status = st.selectbox(
                "Filter by Status",
                statuses,
            )

        filtered_agents_df = agents_df.copy()

        if selected_business_unit != "All":
            filtered_agents_df = filtered_agents_df[
                filtered_agents_df["business_unit"] == selected_business_unit
            ]

        if selected_risk_tier != "All":
            filtered_agents_df = filtered_agents_df[
                filtered_agents_df["risk_tier"] == selected_risk_tier
            ]

        if selected_status != "All":
            filtered_agents_df = filtered_agents_df[
                filtered_agents_df["status"] == selected_status
            ]

        agent_registry_columns = [
            "agent_name",
            "agent_id",
            "business_unit",
            "owner_team",
            "risk_tier",
            "status",
            "model_name",
            "approved_tools",
            "allowed_data_types",
            "data_sensitivity",
            "source_system",
            "created_timestamp",
        ]

        available_agent_columns = [
            col for col in agent_registry_columns
            if col in filtered_agents_df.columns
        ]

        st.dataframe(
            filtered_agents_df[available_agent_columns],
            use_container_width=True,
            hide_index=True,
        )

        download_button(
            filtered_agents_df,
            "agent_registry.csv",
            "Download Agent Registry",
        )


# ===================================================================
# TAB 4 — TOOL REGISTRY
# ===================================================================

with tabs[3]:

    st.header("Tool Registry")

    st.markdown(
        "Governed enterprise tools available to AI agents, including "
        "data sensitivity and PII access indicators."
    )

    if tools_df.empty:
        st.info("No tools available.")

    else:
        tool_col1, tool_col2, tool_col3, tool_col4 = st.columns(4)

        with tool_col1:
            sensitivity_levels = ["All"] + sorted(
                tools_df["sensitivity_level"].dropna().unique().tolist()
            )

            selected_sensitivity = st.selectbox(
                "Filter by Sensitivity",
                sensitivity_levels,
            )

        with tool_col2:
            pii_filter = st.selectbox(
                "PII Access",
                ["All", "True", "False"],
            )

        with tool_col3:
            approval_filter = st.selectbox(
                "Approval Required",
                ["All", "True", "False"],
            )

        with tool_col4:
            tool_statuses = ["All"] + sorted(
                tools_df["status"].dropna().unique().tolist()
            )

            selected_tool_status = st.selectbox(
                "Filter by Tool Status",
                tool_statuses,
            )

        filtered_tools_df = tools_df.copy()

        if selected_sensitivity != "All":
            filtered_tools_df = filtered_tools_df[
                filtered_tools_df["sensitivity_level"] == selected_sensitivity
            ]

        if pii_filter != "All":
            pii_value = pii_filter == "True"
            filtered_tools_df = filtered_tools_df[
                filtered_tools_df["pii_access"] == pii_value
            ]

        if approval_filter != "All":
            approval_value = approval_filter == "True"
            filtered_tools_df = filtered_tools_df[
                filtered_tools_df["approval_required"] == approval_value
            ]

        if selected_tool_status != "All":
            filtered_tools_df = filtered_tools_df[
                filtered_tools_df["status"] == selected_tool_status
            ]

        tool_registry_columns = [
            "tool_display_name",
            "tool_id",
            "tool_name",
            "tool_type",
            "allowed_departments",
            "sensitivity_level",
            "approval_required",
            "pii_access",
            "status",
            "source_system",
            "created_timestamp",
            "approval_timestamp",
            "approved_by",
        ]

        available_tool_columns = [
            col for col in tool_registry_columns
            if col in filtered_tools_df.columns
        ]

        st.dataframe(
            filtered_tools_df[available_tool_columns],
            use_container_width=True,
            hide_index=True,
        )

        download_button(
            filtered_tools_df,
            "tool_registry.csv",
            "Download Tool Registry",
        )


# ===================================================================
# TAB 5 — AI RUNTIME EVENTS
# ===================================================================

with tabs[4]:

    st.header("AI Runtime Events")

    st.markdown(
        "Recent AI runtime requests, governance decisions, risk scores, "
        "latency, model usage, and triggered rules."
    )

    if events_df.empty:
        st.info("No AI runtime events available.")

    else:
        runtime_col1, runtime_col2, runtime_col3, runtime_col4, runtime_col5 = (
            st.columns(5)
        )

        with runtime_col1:
            runtime_agent_options = ["All"] + sorted(
                events_df["agent_id"].dropna().unique().tolist()
            )

            selected_event_agent = st.selectbox(
                "Filter by Agent",
                runtime_agent_options,
                key="runtime_agent_filter",
            )

        with runtime_col2:
            selected_event_decision = st.selectbox(
                "Filter by Decision",
                ["All", "Allowed", "Blocked", "Allowed with Review"],
                key="runtime_decision_filter",
            )

        with runtime_col3:
            risk_range = st.slider(
                "Risk Score Range",
                min_value=0.0,
                max_value=1.0,
                value=(0.0, 1.0),
                step=0.05,
                key="runtime_risk_filter",
            )

        with runtime_col4:
            prompt_search = st.text_input(
                "Search Prompt Text",
                key="runtime_prompt_search",
            )

        with runtime_col5:
            selected_event_date = st.date_input(
                "Filter by Event Date",
                value=None,
                key="runtime_date_filter",
            )

        filtered_events_df = apply_event_filters(
            events_df,
            selected_event_agent,
            selected_event_decision,
            risk_range,
            prompt_search,
            selected_event_date,
        )

        runtime_display_columns = [
            "request_id",
            "user_id",
            "agent_name",
            "agent_id",
            "tool_used",
            "prompt",
            "decision",
            "risk_score",
            "risk_band",
            "hallucination_risk_score",
            "latency_ms",
            "tokens_used",
            "model_name",
            "triggered_rules",
            "rag_domain",
            "retrieved_chunk_count",
            "retrieval_latency_seconds",
            "event_timestamp",
            "event_date",
        ]

        available_runtime_columns = [
            col for col in runtime_display_columns
            if col in filtered_events_df.columns
        ]

        st.dataframe(
            filtered_events_df[available_runtime_columns],
            use_container_width=True,
            hide_index=True,
        )

        download_button(
            filtered_events_df,
            "ai_runtime_events.csv",
            "Download Runtime Events",
        )


# ===================================================================
# TAB 6 — BLOCKED EVENTS
# ===================================================================

with tabs[5]:

    st.header("Blocked AI Requests")

    st.markdown(
        "Governance violations, prompt injection attempts, PII exposure "
        "risks, and unauthorized access attempts."
    )

    if blocked_df.empty:
        st.success("No blocked events found.")

    else:
        blocked_col1, blocked_col2, blocked_col3, blocked_col4 = st.columns(4)

        with blocked_col1:
            blocked_agent_options = ["All"] + sorted(
                blocked_df["agent_id"].dropna().unique().tolist()
            )

            selected_blocked_agent = st.selectbox(
                "Filter by Agent",
                blocked_agent_options,
                key="blocked_agent_filter",
            )

        with blocked_col2:
            blocked_risk_range = st.slider(
                "Risk Score Range",
                min_value=0.0,
                max_value=1.0,
                value=(0.0, 1.0),
                step=0.05,
                key="blocked_risk_filter",
            )

        with blocked_col3:
            blocked_prompt_search = st.text_input(
                "Search Blocked Prompt",
                key="blocked_prompt_search",
            )

        with blocked_col4:
            selected_blocked_date = st.date_input(
                "Filter by Event Date",
                value=None,
                key="blocked_date_filter",
            )

        filtered_blocked_df = apply_event_filters(
            blocked_df,
            selected_blocked_agent,
            "Blocked",
            blocked_risk_range,
            blocked_prompt_search,
            selected_blocked_date,
        )

        blocked_display_columns = [
            "request_id",
            "user_id",
            "agent_name",
            "agent_id",
            "tool_used",
            "prompt",
            "decision",
            "risk_score",
            "risk_band",
            "hallucination_risk_score",
            "latency_ms",
            "tokens_used",
            "model_name",
            "triggered_rules",
            "rag_domain",
            "retrieved_chunk_count",
            "retrieval_latency_seconds",
            "event_timestamp",
            "event_date",
        ]

        available_blocked_columns = [
            col for col in blocked_display_columns
            if col in filtered_blocked_df.columns
        ]

        st.dataframe(
            filtered_blocked_df[available_blocked_columns],
            use_container_width=True,
            hide_index=True,
        )

        download_button(
            filtered_blocked_df,
            "blocked_ai_events.csv",
            "Download Blocked Events",
        )


# ===================================================================
# TAB 7 — GOVERNANCE AUDIT REPORT
# ===================================================================

with tabs[6]:

    st.header("Governance Audit Report")

    st.markdown(
        "Download an audit-ready governance report containing AI runtime events, "
        "risk scores, triggered rules, RAG metadata, and governance decisions."
    )

    if events_df.empty:
        st.info("No runtime events available for audit export.")

    else:
        audit_columns = [
            "request_id",
            "user_id",
            "agent_name",
            "agent_id",
            "tool_used",
            "prompt",
            "decision",
            "risk_score",
            "risk_band",
            "hallucination_risk_score",
            "triggered_rules",
            "rag_domain",
            "retrieved_chunk_count",
            "retrieval_latency_seconds",
            "latency_ms",
            "tokens_used",
            "model_name",
            "event_timestamp",
            "response_timestamp",
            "source_system",
        ]

        available_audit_columns = [
            col for col in audit_columns
            if col in events_df.columns
        ]

        audit_df = events_df[
            available_audit_columns
        ].copy()

        st.subheader("Audit Report Preview")

        st.dataframe(
            audit_df,
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("---")

        download_button(
            audit_df,
            "governance_audit_report.csv",
            "Download Governance Audit Report CSV",
        )
