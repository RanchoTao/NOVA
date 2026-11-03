"""Diverse assumption/operator proposals. Generation is not scientific validation."""
from __future__ import annotations

import hashlib
import json
import random
from typing import Protocol

from .catalog import OPERATORS, load_seeds
from .models import IdeaCard
from .prompting import SYSTEM_PROMPT, creation_prompt


class JSONModel(Protocol):
    def complete_json(self, system: str, user: str) -> dict: ...


def _uid(seed_id: str, operator_id: str, question: str) -> str:
    digest = hashlib.sha256(f"{seed_id}|{operator_id}|{question}".encode("utf-8")).hexdigest()[:12]
    return f"NOVA-{digest.upper()}"


def _validate_model_result(result: dict) -> dict:
    required = ("title", "question", "mechanism", "why_surprising", "minimal_experiment", "baseline", "falsifier")
    if any(not isinstance(result.get(key), str) or not result[key].strip() for key in required):
        raise ValueError("model response missing required textual fields")
    risks = result.get("confounders")
    if not isinstance(risks, list) or not 2 <= len(risks) <= 5 or not all(isinstance(x, str) and x.strip() for x in risks):
        raise ValueError("model response must contain 2-5 concrete confounders")
    return {**{k: result[k].strip() for k in required}, "confounders": risks}


class NovaEngine:
    def __init__(self, model: JSONModel | None = None):
        self.model = model
        self.seeds = load_seeds()

    def roll(self, *, count: int = 3, seed: int | None = None,
             domain: str | None = None, operator: str | None = None) -> list[IdeaCard]:
        if not 1 <= count <= 20:
            raise ValueError("count must be in 1..20")
        if operator is not None and operator not in OPERATORS:
            raise ValueError(f"unknown operator: {operator}")
        options = [s for s in self.seeds if domain is None or s["domain"] == domain]
        if not options:
            raise ValueError(f"unknown domain: {domain}")
        rng = random.Random(seed)
        pairs = [(s, op) for s in options for op in (OPERATORS if operator is None else [operator])]
        rng.shuffle(pairs)
        if count > len(pairs):
            raise ValueError(f"count={count} exceeds {len(pairs)} distinct seed/operator combinations")
        # Greedy diversity: favor unseen operator and domain before reusing either.
        selected: list[tuple[dict, str]] = []
        used_ops: set[str] = set()
        used_domains: set[str] = set()
        used_seeds: set[str] = set()
        while len(selected) < count:
            choice = max(pairs, key=lambda p: (4 * (p[1] not in used_ops)
                                               + 3 * (p[0]["domain"] not in used_domains)
                                               + 2 * (p[0]["id"] not in used_seeds)))
            pairs.remove(choice)
            selected.append(choice)
            used_ops.add(choice[1])
            used_domains.add(choice[0]["domain"])
            used_seeds.add(choice[0]["id"])
        return [self._make_card(s, op) for s, op in selected]

    def _make_card(self, seed: dict, operator_id: str) -> IdeaCard:
        op = OPERATORS[operator_id]
        if self.model is None:
            question = op["question"].format(**seed)
            attrs = {
                "title": f"{op['label']}：{seed['goal']}",
                "question": question,
                "mechanism": op["mechanism"].format(**seed),
                "why_surprising": seed["why_surprising"],
                "minimal_experiment": seed["experiment"],
                "baseline": seed["baseline"],
                "falsifier": seed["falsifier"],
                "confounders": seed["confounders"],
            }
        else:
            raw = self.model.complete_json(SYSTEM_PROMPT, creation_prompt(seed, operator_id, op))
            attrs = _validate_model_result(raw)
        return IdeaCard(
            id=_uid(seed["id"], operator_id, attrs["question"]),
            seed_id=seed["id"], operator_id=operator_id, domain=seed["domain"],
            source_assumption=seed["assumption"],
            origin="model-unverified" if self.model else "template-demo", **attrs,
        )


def artifact(cards: list[IdeaCard]) -> dict:
    return {"format": "nova.idea_batch", "version": "0.1", "scientific_evidence": False,
            "novelty_verified": False, "ideas": [card.to_dict() for card in cards]}


def dump_json(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
