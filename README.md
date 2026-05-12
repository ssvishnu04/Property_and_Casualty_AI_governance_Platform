# Enterprise AI Governance & Observability Platform
### Insurance & Reinsurance (P&C Domain)

![Python](https://img.shields.io/badge/Python-3.10-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-API-green)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red)
![LangChain](https://img.shields.io/badge/LangChain-RAG-orange)
![Azure](https://img.shields.io/badge/Azure-Cloud-blue)
![Databricks](https://img.shields.io/badge/Databricks-Lakehouse-red)
![FAISS](https://img.shields.io/badge/FAISS-VectorSearch-purple)
![MLflow](https://img.shields.io/badge/MLflow-MLOps-lightblue)

Enterprise-style AI Governance & Observability Platform designed for Property & Casualty (P&C) Insurance and Reinsurance environments, demonstrating governance aware AI orchestration, runtime monitoring, AI risk scoring, auditability, and Responsible AI controls for Generative AI and Retrieval Augmented Generation (RAG) systems.

# Project Link

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-governance-platform-property-and-casualty.streamlit.app/)

---

# Executive Summary

The Enterprise AI Governance & Observability Platform is a production style multi agent AI governance solution designed for Property & Casualty (P&C) Insurance and Reinsurance environments.

The platform demonstrates how organizations can securely deploy and monitor Generative AI, Retrieval Augmented Generation (RAG), and AI orchestration workflows while enforcing runtime governance, auditability, AI risk monitoring, and responsible AI controls.

This project simulates enterprise AI governance patterns commonly required in regulated industries such as:
- Insurance
- Reinsurance
- Banking
- Financial Services
- Healthcare

The platform combines:
- Multi agent AI workflows
- Governance aware RAG pipelines
- Runtime monitoring
- AI risk scoring
- Governance audit logging
- Explainable AI workflows
- AI observability dashboards
- Human review workflows

---

# Business Problem

As enterprises operationalize Generative AI and AI orchestration systems, they face significant governance and operational risks:

- Unauthorized AI tool access
- Sensitive data exposure
- Prompt manipulation attempts
- Hallucinated AI responses
- Missing runtime monitoring
- Lack of governance auditability
- Regulatory compliance exposure
- Uncontrolled AI decision workflows

Property & Casualty insurance organizations are especially sensitive due to:
- Policyholder PII
- Claims confidentiality
- Financial risk exposure
- Underwriting model sensitivity
- Reinsurance treaty confidentiality
- Regulatory reporting obligations

This platform demonstrates how enterprise AI systems can be governed safely through runtime governance and observability workflows.

---

# Enterprise Solution Architecture

## Core Architecture Components

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| API Layer | FastAPI |
| Vector Search | FAISS |
| Embeddings | HuggingFace Sentence Transformers |
| LLM | Groq Llama |
| Runtime Governance | Rule-Based Governance Framework |
| RAG Evaluation | RAGAS + Custom Evaluation Pipelines |
| Analytics | Plotly |
| Data Processing | Pandas |
| Runtime Logging | JSON Runtime Events |
| Deployment | Local / Streamlit Cloud |

---
# Enterprise Features

- Runtime AI governance workflows
- Governance aware RAG pipelines
- AI observability dashboards
- Multi agent orchestration
- Runtime risk scoring
- Governance audit logging
- Prompt validation workflows
- Explainable AI responses
- Human review workflows
- Cloud ready deployment architecture

---

# Multi Agent AI Platform

The platform includes multiple governed AI agents:

| Agent | Purpose |
|---|---|
| Claims Summary Agent | Claims triage, reserve review, litigation exposure analysis |
| Policy Coverage Agent | Coverage interpretation and exclusion analysis |
| Underwriting Copilot | Risk evaluation and underwriting assessment |
| CAT Event Intelligence Agent | Catastrophe event analysis and impact assessment |
| Reinsurance Treaty Agent | Treaty review and reinsurance exposure analysis |
| Governance Oversight Agent | Runtime governance monitoring and auditability |

Each agent:
- Uses domain-specific RAG
- Operates under governance controls
- Generates runtime audit events
- Uses approved retrieval workflows
- Supports explainable AI responses

---

# Governance Capabilities

## Runtime Governance Enforcement

The governance framework evaluates every AI request for:

- Sensitive data extraction attempts
- Unauthorized tool usage
- Credential extraction requests
- Internal model exposure requests
- Confidential reinsurance data requests
- Policy violation attempts
- Prompt validation failures
- Governance risk indicators

---

# Governance Decisioning

Requests are dynamically classified into:

| Decision | Meaning |
|---|---|
| Allowed | Low-risk request |
| Allowed with Review | Moderate-risk request requiring governance review |
| Blocked | High-risk or policy-violating request |

---

# Runtime AI Risk Scoring

Each AI request receives:
- Governance risk score
- Risk level classification
- Triggered governance rules
- Runtime audit metadata
- Governance decision tracking

---
# Enterprise RAG Workflow

```text
User submits request
        ↓
Governance evaluation
        ↓
Risk scoring & policy validation
        ↓
Allowed / Review / Blocked
        ↓
Domain-specific RAG retrieval
        ↓
FAISS semantic vector search
        ↓
LLM response generation
        ↓
Governed AI response
        ↓
Runtime audit logging
        ↓
Governance observability dashboard
```

---

# Runtime Governance Workflow

```text
User Prompt
    ↓
Governance Evaluation
    ↓
Risk Scoring
    ↓
Allowed / Review / Blocked
    ↓
RAG Retrieval
    ↓
LLM Response Generation
    ↓
Runtime Audit Logging
    ↓
Governance Analytics Dashboard
```

---

# Governance Analytics Dashboard

The Streamlit dashboard includes:

## Executive Governance Overview
![Executive Dashboard](data/Images/ExecutiveGovernance_1.jpg)

## Runtime Governance KPIs
![Executive Dashboard](data/Images/ExecutiveGovernance_2.jpg)

## AI Evaluation Metrics
![Executive Dashboard](data/Images/AI_Gateway_PlayGround.jpg)

## AI Runtime Events
![Executive Dashboard](data/Images/RunTimeEvents.jpg)

## Blocked Event Monitoring
![Executive Dashboard](data/Images/BlockedEvents.jpg)

## Agent Registry
![Executive Dashboard](data/Images/AI_Agent_Registry.jpg)

## Tool Registry
![Executive Dashboard](data/Images/ToolRegistry.jpg)

## Governance Audit CSV Export
![Executive Dashboard](data/Images/GovernanceAuditReport.jpg)

---
# Sample Governance Scenarios

- PII extraction attempts
- Unauthorized underwriting model access
- Sensitive treaty exposure requests
- Claims data governance validation
- Governance-aware AI review workflows
- Runtime AI risk monitoring

---

# Deployment Options

The platform supports:
- Local development deployment
- Streamlit Cloud deployment
- Azure-ready architecture patterns
- Cloud-native API integration workflows

---

# Disclaimer

This project is intended for:
- Educational purposes
- Portfolio demonstrations
- Enterprise AI governance simulations

No real customer, claims, policyholder, underwriting, or treaty data is used.

---

# Author

Vishnu Yadavalli

---
⭐ Enterprise style AI governance and observability platform demonstrating practical governance aware AI implementation patterns for regulated industries.
