"""Formatting utilities — converts JSON analysis dicts to markdown tables."""
from __future__ import annotations

import json

import pandas as pd


def analysis_json_to_table(analysis_json: dict | str) -> str:
    """Convert a per-skill JSON analysis dict to a markdown table + examples/insight.

    The JSON schema expected (per agent-contract.md):
        {
          "skill": "<skill_id>",
          "metrics": { "<metric_name>": <value>, ... },
          "examples": ["<example_1>", "<example_2>", "<example_3>"],
          "insight": "<one sentence summary>"
        }

    Returns:
        A markdown string with the metrics table, examples, and insight.
    """
    if isinstance(analysis_json, str):
        try:
            analysis_json = json.loads(analysis_json)
        except json.JSONDecodeError:
            return f"_Unable to parse analysis JSON._\n\n```\n{analysis_json}\n```"

    skill_id = analysis_json.get("skill", "")
    metrics: dict = analysis_json.get("metrics", {})
    examples: list = analysis_json.get("examples", [])
    insight: str = analysis_json.get("insight", "")

    parts: list[str] = []

    if skill_id:
        parts.append(f"**Skill**: `{skill_id}`\n")

    # Metrics table
    if metrics:
        rows = [{"Metric": k, "Value": v} for k, v in metrics.items()]
        df = pd.DataFrame(rows)
        parts.append(df.to_markdown(index=False))
    else:
        parts.append("_No numeric metrics available._")

    # Examples
    if examples:
        parts.append("\n**Examples**:")
        for ex in examples:
            parts.append(f"- {ex}")

    # Insight
    if insight:
        parts.append(f"\n**Insight**: {insight}")

    return "\n".join(parts)


def skill_results_to_markdown_table(skill_results: list[dict]) -> str:
    """Convert a list of skill result score dicts to a summary markdown table.

    Each dict expects: skill_id, skill_label, normalized_score, rationale.
    """
    if not skill_results:
        return "_No skill results._"
    rows = [
        {
            "Skill ID": sr.get("skill_id", ""),
            "Label": sr.get("skill_label", ""),
            "Score": round(sr.get("normalized_score", 0.0), 2),
            "Rationale": sr.get("rationale", ""),
        }
        for sr in skill_results
    ]
    df = pd.DataFrame(rows)
    return df.to_markdown(index=False)
