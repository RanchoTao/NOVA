"""Stable, JSON-serializable research artifacts. No scientific verdict is inferred."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

SCHEMA_VERSION = "0.1"


@dataclass(frozen=True)
class IdeaCard:
    id: str
    seed_id: str
    operator_id: str
    domain: str
    title: str
    question: str
    mechanism: str
    why_surprising: str
    minimal_experiment: str
    baseline: str
    falsifier: str
    confounders: list[str]
    source_assumption: str
    origin: str = "template-demo"
    status: str = "IDEA"
    novelty_status: str = "UNCHECKED"
    evidence: list[dict[str, Any]] = field(default_factory=list)
    schema_version: str = SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "IdeaCard":
        if not isinstance(data, dict):
            raise ValueError("idea card must be a JSON object")
        required = (
            "id", "seed_id", "operator_id", "domain", "title", "question",
            "mechanism", "why_surprising", "minimal_experiment", "baseline",
            "falsifier", "confounders", "source_assumption",
        )
        missing = [key for key in required if not data.get(key)]
        if missing:
            raise ValueError(f"missing required card fields: {', '.join(missing)}")
        if not isinstance(data["confounders"], list) or not all(
            isinstance(x, str) and x.strip() for x in data["confounders"]
        ):
            raise ValueError("confounders must be a nonempty list of nonempty strings")
        if data.get("status", "IDEA") not in {"IDEA", "REVIEW_PENDING", "HOLD", "KILL"}:
            raise ValueError("invalid status in v0.1; verified verdicts need external evidence")
        if data.get("novelty_status", "UNCHECKED") != "UNCHECKED":
            raise ValueError("v0.1 cannot certify novelty")
        allowed = set(cls.__dataclass_fields__)
        return cls(**{k: v for k, v in data.items() if k in allowed})


@dataclass(frozen=True)
class ChallengeReport:
    idea_id: str
    status: str
    scientific_verdict: str
    claims_not_verified: list[str]
    confounders: list[str]
    falsification_plan: str
    nearest_neighbor_check: str
    additional_critique: str = ""
    schema_version: str = SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
