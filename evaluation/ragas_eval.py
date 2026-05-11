"""
ragas_eval.py

Purpose:
Enterprise RAG + Governance evaluation framework
without external RAGAS dependency conflicts.

This evaluator measures:
- faithfulness approximation
- answer relevancy approximation
- context precision approximation
- context recall approximation
- governance decision accuracy

Outputs:
- detailed JSON results
- summary JSON metrics
"""

import json
from pathlib import Path
from datetime import datetime

import pandas as pd

from rag.multi_rag_service import ask_rag_question

from api.models.governance_models import (
    GovernanceEvaluationRequest,
)

from api.services.guardrail_service import (
    evaluate_governance_request,
)

from api.services.agent_service import (
    get_agent_by_id,
)


TESTSET_PATH = Path("evaluation/ragas_testset.json")
RESULTS_DIR = Path("evaluation/evaluation_results")


def load_testset() -> list[dict]:
    if not TESTSET_PATH.exists():
        raise FileNotFoundError(
            f"Missing testset file: {TESTSET_PATH}"
        )

    with open(TESTSET_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def tokenize(text: str) -> set:
    if not text:
        return set()

    return set(
        word.lower().strip(".,!?;:()[]{}\"'")
        for word in text.split()
        if word.strip()
    )


def calculate_overlap_score(source_words: set, target_words: set) -> float:
    if not source_words or not target_words:
        return 0.0

    overlap = source_words.intersection(target_words)

    return round(len(overlap) / len(target_words), 4)


def calculate_faithfulness(answer: str, contexts: list[str]) -> float:
    answer_words = tokenize(answer)
    context_words = tokenize(" ".join(contexts))

    return calculate_overlap_score(answer_words, context_words)


def calculate_answer_relevancy(answer: str, ground_truth: str) -> float:
    answer_words = tokenize(answer)
    ground_truth_words = tokenize(ground_truth)

    return calculate_overlap_score(answer_words, ground_truth_words)


def calculate_context_precision(
    contexts: list[str],
    expected_topics: list[str],
) -> float:
    context_words = tokenize(" ".join(contexts))
    topic_words = tokenize(" ".join(expected_topics))

    return calculate_overlap_score(context_words, topic_words)


def calculate_context_recall(
    answer: str,
    expected_topics: list[str],
) -> float:
    answer_words = tokenize(answer)
    topic_words = tokenize(" ".join(expected_topics))

    return calculate_overlap_score(answer_words, topic_words)


def get_default_tool_for_agent(agent_id: str) -> str:
    """
    Uses the first approved tool from agents.json.

    This prevents false unauthorized_tool_access errors
    when agent IDs or tool mappings change.
    """

    agent = get_agent_by_id(agent_id)

    if not agent:
        return "unknown_tool"

    approved_tools = agent.get("approved_tools", [])

    if isinstance(approved_tools, list) and approved_tools:
        return approved_tools[0]

    return "unknown_tool"


def evaluate_rag_quality(testset: list[dict]) -> pd.DataFrame:
    rows = []

    for test_case in testset:

        if test_case.get("expected_decision") == "Blocked":
            continue

        question = test_case["question"]
        domain = test_case["domain"]
        ground_truth = test_case["ground_truth"]
        expected_topics = test_case.get("expected_topics", [])

        print(
            f"Running RAG evaluation: "
            f"{test_case.get('test_id')} | {domain}"
        )

        rag_result = ask_rag_question(
            domain=domain,
            question=question,
        )

        answer = rag_result.get("answer", "")

        contexts = [
            doc.page_content
            for doc in rag_result.get("source_documents", [])
        ]

        rows.append(
            {
                "test_id": test_case.get("test_id"),
                "agent_id": test_case.get("agent_id"),
                "agent_name": test_case.get("agent_name"),
                "domain": domain,
                "evaluation_type": test_case.get("evaluation_type"),
                "question": question,
                "ground_truth": ground_truth,
                "generated_answer": answer,
                "retrieved_chunk_count": rag_result.get(
                    "retrieved_chunk_count",
                    0,
                ),
                "retrieval_latency_seconds": rag_result.get(
                    "retrieval_latency_seconds",
                    0,
                ),
                "faithfulness_score": calculate_faithfulness(
                    answer,
                    contexts,
                ),
                "answer_relevancy_score": calculate_answer_relevancy(
                    answer,
                    ground_truth,
                ),
                "context_precision_score": calculate_context_precision(
                    contexts,
                    expected_topics,
                ),
                "context_recall_score": calculate_context_recall(
                    answer,
                    expected_topics,
                ),
            }
        )

    return pd.DataFrame(rows)


def evaluate_governance(testset: list[dict]) -> pd.DataFrame:
    rows = []

    for test_case in testset:

        request = GovernanceEvaluationRequest(
            user_id="EVAL-USER",
            agent_id=test_case["agent_id"],
            tool_name=get_default_tool_for_agent(
                test_case["agent_id"]
            ),
            prompt=test_case["question"],
        )

        result = evaluate_governance_request(request)

        expected_decision = test_case.get("expected_decision")
        actual_decision = result.decision

        rows.append(
            {
                "test_id": test_case.get("test_id"),
                "agent_id": test_case.get("agent_id"),
                "agent_name": test_case.get("agent_name"),
                "question": test_case.get("question"),
                "expected_decision": expected_decision,
                "actual_decision": actual_decision,
                "decision_match": expected_decision == actual_decision,
                "risk_score": result.risk_score,
                "risk_level_actual": result.risk_level,
                "triggered_rules": result.triggered_rules,
            }
        )

    return pd.DataFrame(rows)


def build_rag_summary(rag_df: pd.DataFrame) -> dict:
    if rag_df.empty:
        return {}

    return {
        "average_faithfulness_score": round(
            float(rag_df["faithfulness_score"].mean()),
            4,
        ),
        "average_answer_relevancy_score": round(
            float(rag_df["answer_relevancy_score"].mean()),
            4,
        ),
        "average_context_precision_score": round(
            float(rag_df["context_precision_score"].mean()),
            4,
        ),
        "average_context_recall_score": round(
            float(rag_df["context_recall_score"].mean()),
            4,
        ),
        "average_retrieved_chunk_count": round(
            float(rag_df["retrieved_chunk_count"].mean()),
            4,
        ),
        "average_retrieval_latency_seconds": round(
            float(rag_df["retrieval_latency_seconds"].mean()),
            4,
        ),
    }


def build_governance_summary(governance_df: pd.DataFrame) -> dict:
    if governance_df.empty:
        return {}

    return {
        "governance_pass_rate": round(
            float(governance_df["decision_match"].mean()),
            4,
        ),
        "average_governance_risk_score": round(
            float(governance_df["risk_score"].mean()),
            4,
        ),
        "total_tests": int(len(governance_df)),
        "passed_tests": int(governance_df["decision_match"].sum()),
        "failed_tests": int(
            len(governance_df)
            - governance_df["decision_match"].sum()
        ),
    }


def save_outputs(
    rag_df: pd.DataFrame,
    governance_df: pd.DataFrame,
) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    rag_detail_path = (
        RESULTS_DIR / f"rag_quality_{timestamp}.json"
    )

    governance_detail_path = (
        RESULTS_DIR / f"governance_quality_{timestamp}.json"
    )

    rag_summary_path = (
        RESULTS_DIR / f"rag_summary_{timestamp}.json"
    )

    governance_summary_path = (
        RESULTS_DIR / f"governance_summary_{timestamp}.json"
    )

    rag_summary = build_rag_summary(rag_df)
    governance_summary = build_governance_summary(governance_df)

    rag_df.to_json(
        rag_detail_path,
        orient="records",
        indent=4,
    )

    governance_df.to_json(
        governance_detail_path,
        orient="records",
        indent=4,
    )

    with open(rag_summary_path, "w", encoding="utf-8") as file:
        json.dump(rag_summary, file, indent=4)

    with open(governance_summary_path, "w", encoding="utf-8") as file:
        json.dump(governance_summary, file, indent=4)

    print("\nSaved Evaluation Outputs")
    print("=" * 80)
    print(f"RAG detailed: {rag_detail_path}")
    print(f"Governance detailed: {governance_detail_path}")
    print(f"RAG summary: {rag_summary_path}")
    print(f"Governance summary: {governance_summary_path}")

    print("\nRAG Summary Metrics")
    print("=" * 80)
    print(json.dumps(rag_summary, indent=4))

    print("\nGovernance Summary Metrics")
    print("=" * 80)
    print(json.dumps(governance_summary, indent=4))


def run_enterprise_evaluation():
    testset = load_testset()

    print("\nRunning enterprise RAG evaluation...")
    rag_df = evaluate_rag_quality(testset)

    print("\nRunning governance evaluation...")
    governance_df = evaluate_governance(testset)

    save_outputs(
        rag_df=rag_df,
        governance_df=governance_df,
    )

    print("\nEnterprise evaluation complete.")


if __name__ == "__main__":
    run_enterprise_evaluation()