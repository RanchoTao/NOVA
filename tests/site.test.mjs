import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import {
  OPERATORS, validateSeeds, generateIdeas, challengeIdea, handoffIdea,
  interpolate, DOMAIN_LABELS
} from "../docs/engine.mjs";

const seeds = JSON.parse(readFileSync(fileURLToPath(new URL("../docs/seeds.json", import.meta.url)), "utf8"));

test("published assumption catalog is valid and complete", () => {
  assert.equal(validateSeeds(seeds), seeds);
  assert.equal(seeds.length, 8);
  assert.equal(Object.keys(OPERATORS).length, 6);
  assert.ok(seeds.every(s => DOMAIN_LABELS[s.domain]));
});

test("a roll produces a diverse unverified scientific batch", () => {
  const batch = generateIdeas(seeds, { count: 5, seed: 42 });
  assert.equal(batch.ideas.length, 5);
  assert.equal(batch.format, "nova.idea_batch");
  assert.equal(batch.novelty_verified, false);
  assert.equal(batch.scientific_evidence, false);
  assert.equal(new Set(batch.ideas.map(c => c.id)).size, 5);
  assert.equal(new Set(batch.ideas.map(c => c.operator_id)).size, 5);
  for (const card of batch.ideas) {
    assert.equal(card.status, "IDEA");
    assert.equal(card.origin, "template-demo");
    assert.equal(card.novelty_status, "UNCHECKED");
    assert.ok(card.question.endsWith("？"));
    assert.ok(card.confounders.length >= 2);
    assert.deepEqual(card.evidence, []);
  }
});

test("seeded rolls are reproducible without history", () => {
  const args = { count: 3, seed: 101 };
  assert.deepEqual(generateIdeas(seeds, args), generateIdeas(seeds, args));
  assert.notDeepEqual(generateIdeas(seeds, { count: 3, seed: 1 }), generateIdeas(seeds, { count: 3, seed: 2 }));
});

test("domain and operator filters respect both constraints", () => {
  const batch = generateIdeas(seeds, { count: 1, domain: "computer-vision", operator: "causal_inverter", seed: 3 });
  assert.equal(batch.ideas.length, 1);
  assert.equal(batch.ideas[0].domain, "computer-vision");
  assert.equal(batch.ideas[0].operator_id, "causal_inverter");
});

test("recent history prioritizes unused combinations", () => {
  const a = generateIdeas(seeds, { count: 3, seed: 5 });
  const history = a.ideas.map(x => x.seed_id + "|" + x.operator_id);
  const b = generateIdeas(seeds, { count: 3, seed: 5, history });
  assert.ok(b.ideas.every(x => !history.includes(x.seed_id + "|" + x.operator_id)));
});

test("all six operators interpolate meaningful fields", () => {
  for (const [op, value] of Object.entries(OPERATORS)) {
    const card = generateIdeas(seeds, { count: 1, operator: op }).ideas[0];
    assert.ok(card.question.length > 20, op);
    assert.ok(card.mechanism.length > 20, op);
    assert.doesNotMatch(card.question, /\{[a-z_]+\}/);
    assert.doesNotMatch(card.mechanism, /\{[a-z_]+\}/);
    assert.ok(interpolate(value.question, seeds[0]));
  }
});

test("critique never certifies novelty or scientific validity", () => {
  const c = generateIdeas(seeds, { count: 1 }).ideas[0];
  const challenge = challengeIdea(c);
  assert.equal(challenge.scientific_verdict, "UNKNOWN");
  assert.equal(challenge.status, "PRELIMINARY_CRITIQUE");
  assert.ok(challenge.claims_not_verified.length >= 2);
  assert.ok(challenge.falsification_plan.includes(c.falsifier));
});

test("handoff is deliberately nonexecuting and unauthorised", () => {
  const c = generateIdeas(seeds, { count: 1 }).ideas[0];
  const result = handoffIdea(c);
  assert.equal(result.format, "nova.ranchoresearch_handoff");
  assert.equal(result.status, "PROPOSED_REVIEW");
  assert.equal(result.execution_authorized, false);
  assert.equal(result.gpu_authorized, false);
  assert.equal(result.publication_authorized, false);
  assert.equal(result.review_required, true);
  assert.equal(result.novelty_status, "UNCHECKED");
});

test("invalid options and catalogs are rejected", () => {
  assert.throws(() => validateSeeds([]));
  assert.throws(() => validateSeeds([seeds[0], seeds[0]]));
  assert.throws(() => generateIdeas(seeds, { count: 0 }));
  assert.throws(() => generateIdeas(seeds, { count: 6 }));
  assert.throws(() => generateIdeas(seeds, { operator: "nonexistent" }));
  assert.throws(() => generateIdeas(seeds, { domain: "nonexistent" }));
  assert.throws(() => generateIdeas(seeds, { count: 2, domain: "computer-vision", operator: "causal_inverter" }));
  assert.throws(() => generateIdeas(seeds, { seed: "not a number" }));
});

test("GitHub Pages entrypoint uses relative assets and no browser API keys", () => {
  const html = readFileSync(fileURLToPath(new URL("../docs/index.html", import.meta.url)), "utf8");
  const app = readFileSync(fileURLToPath(new URL("../docs/app.mjs", import.meta.url)), "utf8");
  assert.match(html, /src="\.\/app\.mjs"/);
  assert.match(html, /href="\.\/styles\.css"/);
  assert.match(app, /fetch\("\.\/seeds\.json"/);
  assert.doesNotMatch(app, /NOVA_API_KEY|Authorization:|Bearer /);
  assert.doesNotMatch(html, /\/api\/roll|\/api\/health/);
});
