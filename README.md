# Enterprise Agentic AI Governance Platform for Insurance & Reinsurance (P&C Domain)

## Overview

The Enterprise Agentic AI Governance Platform is a production-style multi-agent AI governance and observability solution designed for the Property & Casualty (P&C) Insurance and Reinsurance domain.

The platform demonstrates how enterprises can securely operationalize Generative AI, Retrieval-Augmented Generation (RAG), and Agentic AI systems while enforcing governance, runtime monitoring, risk management, auditability, and Responsible AI controls.

This project simulates a real-world enterprise AI governance architecture using:

- Multi-Agent AI workflows
- Domain-specific RAG systems
- Runtime governance enforcement
- Prompt guardrails
- AI risk scoring
- Governance audit logging
- AI evaluation monitoring
- Enterprise analytics dashboards
- governance review workflows

The solution is intentionally designed to resemble enterprise AI governance operating models used by large insurance carriers, reinsurers, financial institutions, and regulated industries.

---

# Business Problem

As organizations deploy enterprise GenAI and Agentic AI systems, they face major operational and governance risks:

- Unauthorized AI tool usage
- Prompt injection attacks
- Sensitive data leakage
- Hallucinated responses
- Lack of runtime AI monitoring
- Missing audit trails
- Regulatory and compliance exposure
- Absence of governance enforcement
- Uncontrolled AI decision-making

Insurance and reinsurance organizations are especially sensitive due to:

- Policyholder PII
- Financial risk exposure
- Reinsurance treaty confidentiality
- Underwriting model sensitivity
- Regulatory reporting requirements
- Claims governance obligations

This platform demonstrates how enterprise AI systems can be governed safely at runtime.

---

# Enterprise Solution Architecture

## Core Architecture Components

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| API Layer | FastAPI |
| Vector Database | FAISS |
| Embeddings | HuggingFace Sentence Transformers |
| LLM | Groq Llama |
| Runtime Governance | Custom Governance Engine |
| RAG Evaluation | Enterprise Evaluation Framework |
| Analytics | Plotly |
| Data Processing | Pandas |
| AI Governance Logging | JSON Runtime Events |
| Deployment | Local / Streamlit Cloud |

---

# Key Features

## Multi-Agent Enterprise AI Platform

The platform contains multiple governed AI agents:

- Claims Summary Agent
- Policy Coverage Agent
- Underwriting Copilot
- CAT Event Intelligence Agent
- Reinsurance Treaty Agent
- Governance Oversight Agent

Each agent:
- Uses domain-specific RAG
- Has approved tool access
- Operates under governance controls
- Generates runtime audit events

---

# Governance Capabilities

## Runtime Governance Enforcement

The governance engine evaluates every request for:

- Prompt injection attacks
- Unauthorized tool access
- PII extraction attempts
- Credential extraction requests
- Sensitive enterprise data requests
- Internal underwriting model exposure
- Confidential reinsurance requests
- Governance bypass attempts

---

## Governance Decisioning

Requests are dynamically classified into:

| Decision | Meaning |
|---|---|
| Allowed | Low-risk request |
| Allowed with Review | Moderate-risk request requiring governance review |
| Blocked | High-risk or policy-violating request |

---

## Runtime AI Risk Scoring

Every request receives:
- AI governance risk score
- Risk level classification
- Triggered governance rules
- Runtime audit metadata

---

# Multi-Agent Architecture

## Claims Summary Agent
Handles claims triage, summaries, reserve review, and litigation exposure analysis.

## Policy Coverage Agent
Provides policy interpretation, coverage analysis, and exclusion review.

## Underwriting Copilot
Evaluates underwriting submissions, catastrophe exposure, and pricing adequacy.

## CAT Event Intelligence Agent
Analyzes catastrophe events, severity projections, and operational impacts.

## Reinsurance Treaty Agent
Reviews treaty structures, attachment points, retention levels, and CAT recoveries.

## Governance Oversight Agent
Monitors enterprise AI governance posture and runtime governance enforcement.

---

# RAG Architecture

## Enterprise RAG Workflow

1. User submits AI request
2. Governance engine evaluates request
3. Approved request routes to domain-specific RAG
4. FAISS retrieves relevant enterprise knowledge
5. LLM generates grounded response
6. Governance metadata logged
7. Runtime event stored for observability and audit

---

# Runtime Governance Workflow

## Governance Pipeline

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

## The Streamlit dashboard includes:

## Executive Governance Overview
![Executive Dashboard](assets/screenshots/executive_dashboard.png)

Runtime Governance KPIs
AI Evaluation Metrics
AI Runtime Events
Blocked Event Monitoring
Agent Registry
Tool Registry
Governance Audit CSV Export

---

# Disclaimer

This project is intended for educational, portfolio, and demonstration purposes only.

No real customer, claims, policyholder, underwriting, or treaty data is used.
