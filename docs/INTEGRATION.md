# RanchoResearch and RanchoControl integration

## Current repo facts verified in November 2026
RanchoResearch publicly documents an `AutoResearchClaw`-derived `researchclaw/` engine, a separate evidence-gate skill and JSON scientific state files. RanchoControl uses an independently versioned task/claim/receipt protocol. NOVA does **not** overwrite either project or assume access to private local files.

## Proposed wire format

`nova handoff ideas.json --idea-id NOVA-... --out handoff.json` emits:

```json
{
  "format": "nova.ranchoresearch_handoff",
  "version": "0.1",
  "status": "PROPOSED_REVIEW",
  "review_required": true,
  "execution_authorized": false,
  "novelty_status": "UNCHECKED",
  "scientific_verdict": "UNKNOWN"
}
```

The full output contains candidate lineage (`candidate_id`, `claim_version`, seed/operator provenance), falsification contract and requested checks. It is **not** the current RanchoControl task schema; do not upload it into `tasks/` as an eligible `READY` item without explicit adaptor review.

## Next implementation milestone
A connector can validate the active `RanchoControl/protocol/WORKER_PROTOCOL.md` and per-project `research-evidence-gate` contract; then translate a `PROPOSED_REVIEW` idea into a specifically addressed research *review* request, record source hashes and actual lease receipts, and only after separate authorization promote an execution task. This should use an isolated feature branch and integration tests with mock control records.
