/**
 * NOVA browser engine — stdlib-only static demo, aligned with the Python v0.1 proposal schema.
 * No model inference, literature search, scientific verification, or network API calls.
 */
export const OPERATORS = {
  necessity_breaker: {
    label: "取消必要条件",
    question: "如果不再依赖“{must}”，能否仍实现“{goal}”？",
    mechanism: "在固定目标与输入信息的条件下移除“{must}”，改用“{object}”；把额外计算、人工规则和监督信息计入总预算。"
  },
  object_switcher: {
    label: "改变操作对象",
    question: "能否绕过“{proxy}”，直接操作“{object}”来实现“{goal}”？",
    mechanism: "把干预点从“{proxy}”移动到“{object}”，用严格消融测量直接操作是否具有独立因果效果。"
  },
  causal_inverter: {
    label: "反转因果解释",
    question: "如果“{failure}”并非能力缺失，而是“{blocker}”，我们能否仅解除阻碍？",
    mechanism: "区分能力不存在和能力存在却未被调用；设计只影响候选阻碍因素的干预，并观察非目标指标。"
  },
  representation_hacker: {
    label: "挑战表示方式",
    question: "把“{representation}”改成“{alternative_representation}”，是否会改变“{goal}”的可解性？",
    mechanism: "保持研究对象的功能或生成机制不变，只改变可计算表示，检验新表示是否带来严格的效率或可辨识性收益。"
  },
  capability_arbitrage: {
    label: "新能力套利",
    question: "已有“{capability}”以后，“{must}”还是“{goal}”的必要条件吗？",
    mechanism: "在相同任务和完整资源账本下，把新可用能力替代原有流程的一环，检查旧设计假设是否过时。"
  },
  anomaly_amplifier: {
    label: "异常放大",
    question: "“{anomaly}”是实验误差，还是揭示一种未描述充分的机制？",
    mechanism: "从最小可复现异常出发，构造区分噪声、测量错误与潜在机制的对照实验，先找反例再扩展解释。"
  }
};

export const DOMAIN_LABELS = {
  "neural-networks": "神经网络",
  "language-models": "大语言模型",
  "computer-vision": "计算机视觉",
  "stochastic-dynamics": "随机动力学",
  "automated-research": "自动科研",
  "machine-learning-theory": "机器学习理论",
  "research-methodology": "科研方法论",
  "reinforcement-learning": "强化学习"
};

const REQUIRED = [
  "id","domain","assumption","must","proxy","object","failure","blocker",
  "representation","alternative_representation","capability","anomaly","goal",
  "experiment","baseline","falsifier","confounders","why_surprising"
];

export function validateSeeds(seeds) {
  if (!Array.isArray(seeds) || seeds.length === 0) throw Error("假设目录为空");
  const seen = new Set();
  for (const seed of seeds) {
    if (!seed || typeof seed !== "object") throw Error("目录结构错误");
    if (REQUIRED.some(k => !seed[k])) throw Error("种子缺少必要字段：" + (seed.id || "UNKNOWN"));
    if (seen.has(seed.id)) throw Error("重复的种子：" + seed.id);
    if (!Array.isArray(seed.confounders) || seed.confounders.length < 2) throw Error("缺少混杂因素");
    seen.add(seed.id);
  }
  return seeds;
}

export function interpolate(pattern, seed) {
  return pattern.replace(/\{([a-z_]+)\}/g, (_, key) => String(seed[key] ?? "{" + key + "}"));
}

function hash32(s) {
  let h = 2166136261;
  for (const ch of s) {
    h ^= ch.codePointAt(0);
    h = Math.imul(h, 16777619);
  }
  return (h >>> 0).toString(16).toUpperCase().padStart(8, "0");
}

function randomGenerator(seed) {
  if (seed === null || seed === undefined || seed === "") return Math.random;
  let s = Number(seed);
  if (!Number.isSafeInteger(s)) throw Error("随机种子必须是整数");
  s = s | 0;
  return function () {
    s += 0x6D2B79F5;
    let t = s;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function shuffle(items, rng) {
  for (let i = items.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    [items[i], items[j]] = [items[j], items[i]];
  }
  return items;
}

export function generateIdeas(seeds, { count = 3, domain = "", operator = "", seed = null, history = [] } = {}) {
  validateSeeds(seeds);
  if (!Number.isInteger(count) || count < 1 || count > 5) throw Error("每轮构想数量必须在 1 到 5 之间");
  if (operator && !Object.hasOwn(OPERATORS, operator)) throw Error("未知的破坏算子");
  const pool = seeds.filter(s => !domain || s.domain === domain);
  if (pool.length === 0) throw Error("当前领域没有假设种子");
  const ops = operator ? [operator] : Object.keys(OPERATORS);
  const rng = randomGenerator(seed);
  const pairs = shuffle(pool.flatMap(s => ops.map(op => ({ s, op }))), rng);
  if (count > pairs.length) throw Error("此筛选条件下可用组合不足，请减少构想数量");
  const selected = [];
  const usedOps = new Set(), usedDomains = new Set(), usedSeeds = new Set(), historySet = new Set(history);
  while (selected.length < count) {
    let bestIndex = 0, score = -Infinity;
    for (let i = 0; i < pairs.length; i++) {
      const p = pairs[i];
      const pairKey = p.s.id + "|" + p.op;
      const rank = 100 * Number(!historySet.has(pairKey))
                 + 4 * Number(!usedOps.has(p.op))
                 + 3 * Number(!usedDomains.has(p.s.domain))
                 + 2 * Number(!usedSeeds.has(p.s.id));
      if (rank > score) { score = rank; bestIndex = i; }
    }
    const pick = pairs.splice(bestIndex, 1)[0];
    selected.push(pick);
    usedOps.add(pick.op);
    usedDomains.add(pick.s.domain);
    usedSeeds.add(pick.s.id);
  }
  const ideas = selected.map(({ s, op }) => {
    const def = OPERATORS[op];
    const question = interpolate(def.question, s);
    return {
      id: "NOVA-WEB-" + hash32(s.id + "|" + op + "|" + question),
      seed_id: s.id, operator_id: op, domain: s.domain,
      title: def.label + "：" + s.goal,
      question, mechanism: interpolate(def.mechanism, s),
      why_surprising: s.why_surprising,
      minimal_experiment: s.experiment,
      baseline: s.baseline,
      falsifier: s.falsifier,
      confounders: [...s.confounders],
      source_assumption: s.assumption,
      origin: "template-demo",
      status: "IDEA", novelty_status: "UNCHECKED",
      evidence: [], schema_version: "0.1"
    };
  });
  return {
    format: "nova.idea_batch", version: "0.1",
    scientific_evidence: false, novelty_verified: false, ideas
  };
}

export function challengeIdea(card) {
  if (!card || !card.id || !card.minimal_experiment) throw Error("无效构想");
  return {
    idea_id: card.id, status: "PRELIMINARY_CRITIQUE", scientific_verdict: "UNKNOWN",
    claims_not_verified: [
      "最近邻文献及方法重合度尚未检索与核验",
      "核心机制未作独立验证",
      "尚无有效实验、重复试验或统计置信区间"
    ],
    confounders: [...card.confounders],
    falsification_plan: card.minimal_experiment + "。反证门槛：" + card.falsifier,
    nearest_neighbor_check: "针对假设、机制和实验范式分别检索最近邻文献；记录确切重合主张与差异，不得仅凭关键词判定原创性。",
    additional_critique: "浏览器演示版没有调用模型或进行实时查新。以上仅为结构化检查清单。",
    schema_version: "0.1"
  };
}

export function handoffIdea(card) {
  if (!card || !card.id || !card.question) throw Error("无效构想");
  return {
    format: "nova.ranchoresearch_handoff", version: "0.1",
    handoff_id: "HO-" + hash32(card.id),
    idea_id: card.id, candidate_id: card.id, claim_version: 1,
    status: "PROPOSED_REVIEW", review_required: true,
    execution_authorized: false, gpu_authorized: false, publication_authorized: false,
    novelty_status: "UNCHECKED", scientific_verdict: "UNKNOWN",
    source: { generator: "NOVA-static", origin: card.origin, seed_id: card.seed_id, operator_id: card.operator_id },
    claim: { title: card.title, hypothesis: card.question, mechanism: card.mechanism, assumption: card.source_assumption },
    preflight: { minimal_experiment: card.minimal_experiment, baseline: card.baseline, falsifier: card.falsifier, confounders: card.confounders },
    requested_checks: [
      "independent nearest-neighbor literature search and claim comparison",
      "research-evidence-gate skill and five-axis claim/version review",
      "cheapest falsification, leakage/resource parity and simple baselines",
      "only after independent authorization: real experiment receipt"
    ],
    integration_note: "Inert proposal only; not a RanchoControl READY task. Receiving worker must validate and authorize independently."
  };
}
