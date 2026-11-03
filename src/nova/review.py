"""Bounded, non-certifying scientific critique and RanchoResearch handoff."""
from __future__ import annotations

import hashlib
import json
from typing import Protocol

from .models import ChallengeReport, IdeaCard
from .prompting import SYSTEM_PROMPT, critique_prompt


class JSONModel(Protocol):
    def complete_json(self, system: str, user: str) -> dict: ...


def challenge(card: IdeaCard, model: JSONModel | None = None) -> ChallengeReport:
    additional = ""
    if model is not None:
        result = model.complete_json(SYSTEM_PROMPT, critique_prompt(card.to_dict()))
        if not isinstance(result.get("critique"), str) or not result["critique"].strip():
            raise ValueError("review model did not return a critique")
        additional = result["critique"][:2500]
    return ChallengeReport(
        idea_id=card.id,
        status="PRELIMINARY_CRITIQUE",
        scientific_verdict="UNKNOWN",
        claims_not_verified=[
            "最近邻文献及方法重合度尚未检索与核验",
            "核心机制未作独立验证",
            "尚无有效实验、重复试验或统计置信区间",
        ],
        confounders=card.confounders,
        falsification_plan=card.minimal_experiment + "。反证门槛：" + card.falsifier,
        nearest_neighbor_check=("针对研究假设、机制和实验范式分别检索最近邻文献与论文；"
                                "记录题目、作者、日期、具体重合主张与差异；"
                                "不得仅凭关键词相似判定重复，也不得凭语言模型印象声明原创。"),
        additional_critique=additional,
    )


def handoff(card: IdeaCard) -> dict:
    """A proposal for evidence review; NEVER an authorized execution task."""
    return {
        "format": "nova.ranchoresearch_handoff", "version": "0.1",
        "handoff_id": "HO-" + hashlib.sha256(card.id.encode()).hexdigest()[:12].upper(),
        "idea_id": card.id,
        "candidate_id": card.id,
        "claim_version": 1,
        "status": "PROPOSED_REVIEW",
        "review_required": True,
        "execution_authorized": False,
        "gpu_authorized": False,
        "publication_authorized": False,
        "novelty_status": "UNCHECKED",
        "scientific_verdict": "UNKNOWN",
        "source": {"generator": "NOVA", "origin": card.origin,
                   "seed_id": card.seed_id, "operator_id": card.operator_id},
        "claim": {"title": card.title, "hypothesis": card.question,
                  "mechanism": card.mechanism, "assumption": card.source_assumption},
        "preflight": {"minimal_experiment": card.minimal_experiment,
                      "baseline": card.baseline, "falsifier": card.falsifier,
                      "confounders": card.confounders},
        "requested_checks": [
            "independent nearest-neighbor literature search and claim comparison",
            "research-evidence-gate skill and five-axis claim/version review",
            "cheapest falsification, leakage/resource parity and simple baselines",
            "only after independent authorization: real experiment receipt",
        ],
        "integration_note": (
            "This is an inert proposal JSON, not a RanchoControl READY task or a runnable "
            "RanchoResearch job. The receiving worker must map it to its validated schema "
            "and permissions and retain evidence provenance."
        ),
    }


def select_card(document: dict, idea_id: str | None = None) -> IdeaCard:
    if document.get("format") == "nova.idea_batch":
        cards = [IdeaCard.from_dict(x) for x in document.get("ideas", [])]
    else:
        cards = [IdeaCard.from_dict(document)]
    if idea_id:
        cards = [card for card in cards if card.id == idea_id]
    if len(cards) != 1:
        raise ValueError(f"choose exactly one idea via --idea-id; matching cards: {len(cards)}")
    return cards[0]


def read_card_file(path: str, idea_id: str | None = None) -> IdeaCard:
    with open(path, "r", encoding="utf-8") as stream:
        data = json.load(stream)
    if not isinstance(data, dict):
        raise ValueError("input JSON must be an object")
    return select_card(data, idea_id)
