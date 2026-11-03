# NOVA architecture v0.1

## Design decision
Separate *divergence* from *verification*. NOVA creates falsifiable provocations; external independent audit decides novelty, mechanism and publication readiness. It is neither a generic paper-title generator nor a fully autonomous scientist.

## Data flow

```text
curated seed catalog (seeds.json)
        +
6 explicit conceptual inversion operators (catalog.py)
        |
        v
NovaEngine.roll(): randomized candidate order + diversity greedy selection
        |
        +-- template-demo: mechanical, reproducible demonstration
        +-- model-unverified: opt-in LLM synthesis via ChatJSONClient
        |
        v
strict IdeaCard schema (models.py)
        |
        +-- challenge: local critique checklist; optional model adversary
        +-- handoff: inert RanchoResearch review request
        +-- localhost UI: safe inspection and export
```

`seed` fixes choice of seed/operator pairs. `NOVA_API_KEY` is required only for the model path. The model is not trusted to assign novelty_status or scientific verdict; those fields are unconditionally set by NOVA.

## Science state
- `IDEA` / `UNCHECKED` is the only automatically generated state.
- `challenge` returns `PRELIMINARY_CRITIQUE` / `UNKNOWN`, never review acceptance.
- `handoff` returns `PROPOSED_REVIEW`, `execution_authorized=false`.
- No real literature retrieval, benchmark runner, lab notebook, async job system or compute scheduler exists in v0.1.

## Why testability is a first-class field
Each idea must specify a concrete observation that could make it fail. This reduces spectacular but untestable descriptions and supports a cheap preflight. Even a model-composed card can hallucinate a sensible-sounding experiment; independently inspect before executing.

## Important future interfaces
- `AssumptionRecord`: source/date/provenance/claim scope and history of falsifications.
- `SearchEvidence`: nearest-neighbor explicit paper claims, not similarity keyword alone.
- `ExperimentContract`: baseline, fixed dataset split, metric, resources, stopping criterion and negative controls.
- `SurpriseEvaluation`: blinded expert judgments + actual falsification outcome; do not optimize a single self-reported score.
- `DiscoveryBenchmark`: time-censored historical rediscovery plus synthetic held-out tasks; mitigate model pretraining contamination.

## Security boundaries
The HTTP service binds only `127.0.0.1`, requires JSON for POST, enforces request sizes and checks `Origin`; it does not expose a shell or remote job runner. The local server is intended for a trusted machine, not internet-facing deployment. For a production service add auth, rate limiting, rate budgets, CSRF defense, provenance store and deployment review. No private research data is included in source distribution.
