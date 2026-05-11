"""
governance_agent.py

Purpose:
Enterprise Governance Oversight Agent powered by
runtime governance analytics and Governance RAG guidance.
"""

from collections import Counter, defaultdict
from statistics import mean

from api.services.event_service import get_all_events
from rag.multi_rag_service import ask_rag_question


def calculate_governance_summary(events: list) -> dict:
    total_requests = len(events)

    allowed_count = 0
    blocked_count = 0
    review_count = 0

    governance_scores = []
    hallucination_scores = []

    rule_counter = Counter()
    agent_risk_scores = defaultdict(list)

    for event in events:
        decision = event.get("decision", "UNKNOWN")

        if decision == "Allowed":
            allowed_count += 1

        elif decision == "Blocked":
            blocked_count += 1

        elif decision == "Allowed with Review":
            review_count += 1

        risk_score = float(event.get("risk_score", 0))
        hallucination_score = float(
            event.get("hallucination_risk_score", 0)
        )

        governance_scores.append(risk_score)
        hallucination_scores.append(hallucination_score)

        triggered_rules = event.get("triggered_rules", [])

        for rule in triggered_rules:
            rule_counter[rule] += 1

        agent_name = event.get(
            "agent_name",
            event.get("agent_id", "Unknown"),
        )

        agent_risk_scores[agent_name].append(risk_score)

    blocked_rate = (
        (blocked_count / total_requests) * 100
        if total_requests > 0
        else 0
    )

    avg_governance_score = (
        mean(governance_scores)
        if governance_scores
        else 0
    )

    avg_hallucination_score = (
        mean(hallucination_scores)
        if hallucination_scores
        else 0
    )

    high_risk_events = len(
        [
            score
            for score in governance_scores
            if score >= 0.75
        ]
    )

    top_rules = rule_counter.most_common(5)

    highest_risk_agents = sorted(
        [
            (
                agent,
                mean(scores),
            )
            for agent, scores in agent_risk_scores.items()
        ],
        key=lambda x: x[1],
        reverse=True,
    )[:5]

    return {
        "total_requests": total_requests,
        "allowed_count": allowed_count,
        "blocked_count": blocked_count,
        "review_count": review_count,
        "blocked_rate": blocked_rate,
        "avg_governance_score": avg_governance_score,
        "avg_hallucination_score": avg_hallucination_score,
        "high_risk_events": high_risk_events,
        "top_rules": top_rules,
        "highest_risk_agents": highest_risk_agents,
    }


def build_governance_summary_text(summary: dict) -> str:
    response = (
        "Enterprise AI Governance Summary:\n\n"
        f"Total Runtime Requests: {summary['total_requests']}\n"
        f"Allowed Requests: {summary['allowed_count']}\n"
        f"Review Required Requests: {summary['review_count']}\n"
        f"Blocked Requests: {summary['blocked_count']}\n"
        f"Blocked Request Rate: {summary['blocked_rate']:.2f}%\n"
        f"High-Risk Events: {summary['high_risk_events']}\n"
        f"Average Governance Risk Score: {summary['avg_governance_score']:.2f}\n"
        f"Average Hallucination Risk Score: {summary['avg_hallucination_score']:.2f}\n\n"
        "Governance Assessment:\n"
    )

    if summary["blocked_rate"] >= 15 or summary["high_risk_events"] >= 5:
        response += (
            "- Governance risk posture requires immediate review.\n"
            "- Elevated unsafe prompt activity detected.\n"
            "- Additional runtime restrictions may be required.\n"
        )

    elif summary["blocked_rate"] >= 5:
        response += (
            "- Governance posture appears stable with moderate risk activity.\n"
            "- Continue runtime monitoring and audit review.\n"
        )

    else:
        response += (
            "- Governance posture appears stable.\n"
            "- Current controls appear effective for runtime monitoring.\n"
        )

    response += "\nTop Triggered Governance Rules:\n"

    if summary["top_rules"]:
        for rule, count in summary["top_rules"]:
            response += f"- {rule}: {count}\n"
    else:
        response += "- No governance rules triggered.\n"

    response += "\nHighest Risk AI Agents:\n"

    if summary["highest_risk_agents"]:
        for agent, avg_score in summary["highest_risk_agents"]:
            response += f"- {agent}: avg risk {avg_score:.2f}\n"
    else:
        response += "- No agent risk activity detected.\n"

    response += (
        "\nRecommended Governance Actions:\n"
        "- Continue runtime monitoring and audit review.\n"
        "- Review hallucination trends across AI agents.\n"
        "- Validate tool authorization mappings.\n"
        "- Monitor sensitive data request activity.\n"
        "- Periodically review AI governance policies and controls.\n"
    )

    return response


def build_rag_metadata(rag_result: dict) -> dict:
    return {
        "rag_domain": "governance",
        "retrieved_sources": rag_result.get("retrieved_sources", []),
        "retrieved_chunk_count": rag_result.get("retrieved_chunk_count", 0),
        "retrieval_latency_seconds": rag_result.get(
            "retrieval_latency_seconds",
            0,
        ),
    }


def run_governance_agent(prompt: str) -> dict:
    events = get_all_events()

    if not events:
        return {
            "response": (
                "Governance Oversight Agent Response:\n\n"
                "No governance runtime events were available."
            ),
            "rag_metadata": {},
        }

    summary = calculate_governance_summary(events)

    governance_summary = build_governance_summary_text(summary)

    rag_result = ask_rag_question(
        domain="governance",
        question=prompt,
    )

    rag_answer = rag_result.get(
        "answer",
        "No governance policy guidance retrieved.",
    )

    rag_sources = rag_result.get("source_documents", [])

    response = (
        "Governance Oversight Agent Response:\n\n"
        f"{governance_summary}\n"
        "\nGovernance Policy Guidance from RAG:\n"
        f"{rag_answer}\n\n"
    )

    if rag_sources:
        response += "Retrieved Governance Sources:\n"

        unique_sources = []

        for doc in rag_sources:
            source = doc.metadata.get("source", "Unknown Source")

            if source not in unique_sources:
                unique_sources.append(source)

        for source in unique_sources:
            response += f"- {source}\n"

    response += (
        "\nGovernance Note:\n"
        "This AI-generated governance summary is advisory and should not replace "
        "formal compliance review, enterprise risk management, "
        "legal oversight, or model governance committee decisions."
    )

    return {
        "response": response,
        "rag_metadata": build_rag_metadata(rag_result),
    }