import {
  OPERATORS, DOMAIN_LABELS, validateSeeds,
  generateIdeas, challengeIdea, handoffIdea
} from "./engine.mjs";

const $ = id => document.getElementById(id);
const FAVORITES_KEY = "nova.favorites.v1";
let catalog = [];
let currentBatch = null;
let currentTab = "current";
let history = [];
let favorites = readFavorites();
let toastTimer;

function el(tag, className = "", text = "") {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function readFavorites() {
  try {
    const value = JSON.parse(localStorage.getItem(FAVORITES_KEY) || "[]");
    return Array.isArray(value) ? value.filter(x => x && typeof x === "object" && x.id && x.question).slice(0, 100) : [];
  } catch { return []; }
}

function persistFavorites() {
  try { localStorage.setItem(FAVORITES_KEY, JSON.stringify(favorites)); }
  catch { toast("当前浏览器禁止本地存储，收藏仅在本页有效"); }
}

function toast(message) {
  const box = $("toast");
  box.textContent = message;
  box.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => box.classList.remove("show"), 3100);
}

function exportJSON(payload, filename) {
  const blob = new Blob([JSON.stringify(payload, null, 2) + "\n"], { type: "application/json;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1200);
}

function contentField(label, text, wide = false) {
  const box = el("div", "card-field" + (wide ? " wide" : ""));
  box.append(el("b", "", label), el("p", "", String(text ?? "—")));
  return box;
}

function action(label, className, onClick) {
  const b = el("button", "card-action " + className, label);
  b.type = "button";
  b.addEventListener("click", onClick);
  return b;
}

async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text);
    toast("已复制命题到剪贴板");
  } catch {
    toast("当前浏览器不支持复制，请使用导出 JSON");
  }
}

function ideaCard(card, index) {
  const root = el("article", "idea-card");
  const top = el("div", "card-top");
  top.append(el("span", "card-id", "CONCEPT " + String(index + 1).padStart(2, "0") + " / " + card.id));
  const flags = el("div", "card-flags");
  flags.append(
    el("span", "flag", DOMAIN_LABELS[card.domain] || card.domain),
    el("span", "flag", OPERATORS[card.operator_id]?.label || card.operator_id),
    el("span", "flag yellow", "未验证 · IDEA")
  );
  top.append(flags);

  root.append(top, el("h3", "card-question", card.question),
    el("p", "card-sup", "挑战预设：" + card.source_assumption),
    el("p", "card-why", card.why_surprising));

  const details = el("div", "card-grid");
  details.append(
    contentField("01 / 候选机制", card.mechanism, true),
    contentField("02 / 最小可证伪实验", card.minimal_experiment, true),
    contentField("03 / 必要基线", card.baseline),
    contentField("04 / 如何推翻它", card.falsifier),
    contentField("05 / 混杂因素", (card.confounders || []).join(" · "), true)
  );
  root.append(details);

  const actions = el("div", "card-actions");
  const isSaved = favorites.some(x => x.id === card.id);
  const save = action(isSaved ? "★ 已收藏" : "☆ 收藏构想", isSaved ? "selected" : "primary", () => {
    if (favorites.some(x => x.id === card.id)) {
      favorites = favorites.filter(x => x.id !== card.id);
      toast("已取消收藏");
    } else {
      favorites = [card, ...favorites].slice(0, 100);
      toast("已保存到本机收藏夹");
    }
    persistFavorites();
    updateFavoriteCount();
    render();
  });
  const challenge = action("⚑ 质疑这个想法", "", () => {
    const opening = review.hidden;
    review.hidden = !opening;
    challenge.textContent = opening ? "⌃ 收起质疑" : "⚑ 质疑这个想法";
  });
  actions.append(
    save, challenge,
    action("复制问题", "", () => copyText(card.question)),
    action("导出交接 JSON ↓", "", () => {
      exportJSON(handoffIdea(card), "nova-handoff-" + card.id + ".json");
      toast("已导出待审计交接提案（不会自动执行）");
    })
  );
  root.append(actions);

  const report = challengeIdea(card);
  const review = el("div", "review-panel");
  review.hidden = true;
  review.append(el("h4", "", "科学怀疑者 · 预审检查（不是实时查新）"));
  review.append(el("p", "", "最小反证：" + report.falsification_plan));
  review.append(el("p", "", "最近邻检索要求：" + report.nearest_neighbor_check));
  const ul = el("ul");
  for (const item of report.claims_not_verified) ul.append(el("li", "", item));
  review.append(ul);
  review.append(el("p", "", report.additional_critique));
  root.append(review);
  return root;
}

function updateFavoriteCount() {
  $("saved-count").textContent = String(favorites.length);
}

function updateTabs() {
  for (const name of ["current", "saved"]) {
    const active = currentTab === name;
    $("tab-" + name).classList.toggle("active", active);
    $("tab-" + name).setAttribute("aria-pressed", String(active));
  }
  $("download-batch").disabled = currentTab !== "current" || !currentBatch;
}

function render() {
  const cards = currentTab === "current" ? (currentBatch?.ideas || []) : favorites;
  $("result-count").textContent = "/ " + cards.length;
  updateTabs();
  const box = $("ideas");
  box.replaceChildren();
  if (!cards.length) {
    const empty = el("div", "empty-state");
    empty.append(
      el("span", "empty-mark", "✳"),
      el("h3", "", currentTab === "saved" ? "你的收藏夹还是空的。" : "下一个好问题，从这里开始。"),
      el("p", "", currentTab === "saved" ? "收藏你希望深入研究的假设，记录只保存在当前浏览器。" : "按下「震撼首发！」，用结构化的概念变换生成可证伪的科研构想。"),
      el("span", "", "没有独立查新 · 没有实际实验 · 没有科学验证")
    );
    box.append(empty);
    return;
  }
  cards.forEach((card, index) => box.append(ideaCard(card, index)));
}

function updateReels(card) {
  $("slot-assumption").textContent = card.source_assumption;
  $("slot-operator").textContent = OPERATORS[card.operator_id]?.label || card.operator_id;
  $("slot-question").textContent = card.question;
}

async function spin(event) {
  event.preventDefault();
  if (!catalog.length) return;
  const button = $("spin");
  button.disabled = true;
  const originalLabel = button.querySelector("span:nth-child(2)");
  originalLabel.textContent = "正在打破默认假设…";
  $("reels").classList.add("spinning");

  try {
    const domain = $("domain").value;
    const operator = $("operator").value;
    const desiredCount = Number($("count").value);
    const pairCount = catalog.filter(s => !domain || s.domain === domain).length * (operator ? 1 : Object.keys(OPERATORS).length);
    const count = Math.min(desiredCount, pairCount);
    if (!count) throw Error("当前条件下没有候选组合");
    if (count < desiredCount) toast("该筛选条件最多包含 " + count + " 个不同组合");
    const seedInput = $("seed").value.trim();
    const seed = seedInput === "" ? null : Number(seedInput);
    const batch = generateIdeas(catalog, { domain, operator, count, seed, history });
    await new Promise(resolve => setTimeout(resolve, 540));
    currentBatch = batch;
    history.push(...batch.ideas.map(x => x.seed_id + "|" + x.operator_id));
    history = history.slice(-60);
    updateReels(batch.ideas[0]);
    currentTab = "current";
    render();
    $("ideas").scrollIntoView({ behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "start" });
  } catch (error) {
    toast("生成失败：" + error.message);
  } finally {
    $("reels").classList.remove("spinning");
    button.disabled = false;
    originalLabel.textContent = "再来一轮！";
  }
}

async function init() {
  updateFavoriteCount();
  $("spin").disabled = true;
  $("controls").addEventListener("submit", spin);
  $("tab-current").addEventListener("click", () => { currentTab = "current"; render(); });
  $("tab-saved").addEventListener("click", () => { currentTab = "saved"; render(); });
  $("download-batch").addEventListener("click", () => {
    if (!currentBatch) return;
    exportJSON(currentBatch, "nova-ideas.json");
    toast("已导出本轮未验证构想");
  });
  try {
    const response = await fetch("./seeds.json", { cache: "no-store" });
    if (!response.ok) throw Error("无法获取假设数据：" + response.status);
    catalog = validateSeeds(await response.json());
    const domains = [...new Set(catalog.map(x => x.domain))].sort();
    for (const domain of domains) {
      const item = el("option", "", DOMAIN_LABELS[domain] || domain);
      item.value = domain;
      $("domain").append(item);
    }
    for (const [key, op] of Object.entries(OPERATORS)) {
      const item = el("option", "", op.label);
      item.value = key;
      $("operator").append(item);
    }
    $("catalog-status").textContent = catalog.length + " 条假设 · " + Object.keys(OPERATORS).length + " 个破坏算子 · " + (catalog.length * Object.keys(OPERATORS).length) + " 种基本组合";
    $("spin").disabled = false;
  } catch (error) {
    $("catalog-status").textContent = "目录加载失败";
    $("ideas").replaceChildren(el("div", "empty-state", "加载失败：" + error.message + "。请通过 GitHub Pages 或本地 HTTP 服务器打开，不要直接双击 HTML 文件。"));
  }
}

init();
