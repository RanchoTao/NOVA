"""A small curated library of assumptions; explicitly not a literature corpus."""
from __future__ import annotations

import json
from importlib.resources import files

OPERATORS: dict[str, dict[str, str]] = {
    "necessity_breaker": {
        "label": "取消必要条件",
        "question": "如果不再依赖“{must}”，能否仍实现“{goal}”？",
        "mechanism": "在固定目标与输入信息的条件下移除“{must}”，改用“{object}”；把额外计算、人工规则和监督信息计入总预算。",
    },
    "object_switcher": {
        "label": "改变操作对象",
        "question": "能否绕过“{proxy}”，直接操作“{object}”来实现“{goal}”？",
        "mechanism": "把干预点从“{proxy}”移动到“{object}”，用严格消融测量直接操作是否具有独立因果效果。",
    },
    "causal_inverter": {
        "label": "反转因果解释",
        "question": "如果“{failure}”并非能力缺失，而是“{blocker}”，我们能否仅解除阻碍？",
        "mechanism": "区分能力不存在和能力存在却未被调用；设计只影响候选阻碍因素的干预，并观察非目标指标。",
    },
    "representation_hacker": {
        "label": "挑战表示方式",
        "question": "把“{representation}”改成“{alternative_representation}”，是否会改变“{goal}”的可解性？",
        "mechanism": "保持研究对象的功能或生成机制不变，只改变可计算表示，检验新表示是否带来严格的效率或可辨识性收益。",
    },
    "capability_arbitrage": {
        "label": "新能力套利",
        "question": "已有“{capability}”以后，“{must}”还是“{goal}”的必要条件吗？",
        "mechanism": "在相同任务和完整资源账本下，把新可用能力替代原有流程的一环，检查旧设计假设是否过时。",
    },
    "anomaly_amplifier": {
        "label": "异常放大",
        "question": "“{anomaly}”是实验误差，还是揭示一种未描述充分的机制？",
        "mechanism": "从最小可复现异常出发，构造区分噪声、测量错误与潜在机制的对照实验，先找反例再扩展解释。",
    },
}

REQUIRED_SEED_KEYS = {
    "id", "domain", "assumption", "must", "proxy", "object", "failure",
    "blocker", "representation", "alternative_representation", "capability",
    "anomaly", "goal", "experiment", "baseline", "falsifier", "confounders",
    "why_surprising",
}


def load_seeds() -> list[dict]:
    seeds = json.loads(files("nova").joinpath("seeds.json").read_text(encoding="utf-8"))
    if not isinstance(seeds, list) or not seeds:
        raise ValueError("seed catalog is empty")
    seen = set()
    for seed in seeds:
        if not isinstance(seed, dict) or REQUIRED_SEED_KEYS - seed.keys():
            raise ValueError(f"invalid catalog entry: {seed!r}")
        if not all(seed[k] for k in REQUIRED_SEED_KEYS):
            raise ValueError(f"blank catalog entry: {seed.get('id')}")
        if seed["id"] in seen:
            raise ValueError(f"duplicate seed id: {seed['id']}")
        seen.add(seed["id"])
    return seeds
