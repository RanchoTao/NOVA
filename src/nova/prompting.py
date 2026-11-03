"""Constrained creative synthesis prompts, explicitly separated from scientific checking."""
from __future__ import annotations

import json

SYSTEM_PROMPT = """You are NOVA's scientific imagination engine. Produce ONE genuinely challenging,
nontrivial, falsifiable scientific hypothesis in Chinese. Do not write a paper title
instead of a scientific question. Attack the assumption rather than performing minor
algorithm recombinations. Explicitly state a causal mechanism and a cheap decisive
experiment. Propose a realistic baseline and concrete falsifier. Never fabricate
citations, verified results, novelty assessments, empirical numbers, or claims about
real papers. Research provenance and scientific validity are UNKNOWN at ideation.
Return a single JSON object with these exact nonempty string keys:
 title, question, mechanism, why_surprising, minimal_experiment, baseline, falsifier
and a confounders array containing 2-5 nonempty strings. No Markdown fences."""


def creation_prompt(seed: dict, operator_id: str, operator: dict) -> str:
    return (
        "Break this assumption using the selected operator. Seek a surprising yet precise "
        "prediction, not a catchy slogan. Avoid assuming the proposed hypothesis is true.\n"
        f"Selected operator: {operator_id} / {operator['label']}\n"
        f"Operator question: {operator['question'].format(**seed)}\n"
        "Research assumption and known design constraints (curated input, not evidence):\n"
        + json.dumps(seed, ensure_ascii=False, sort_keys=True)
    )


def critique_prompt(card: dict) -> str:
    return (
        "Act as an adversarial scientific reviewer. Treat all statements as UNVERIFIED. "
        "Identify simplest explanations, leakage, unfair resources, an obvious baseline, "
        "and the fastest counterexample. Explain what nearest-neighbor literature should "
        "be checked, but do NOT claim you ran a search. "
        "Return JSON with a single key 'critique' containing <=1200 Chinese characters.\n"
        + json.dumps(card, ensure_ascii=False, sort_keys=True)
    )
