# NOVA agent instructions

## Product intent
NOVA is a scientific *idea discovery* workbench. The output is a question to investigate, not a verified paper, novel result or experimental outcome.

## Required scientific boundaries
- **Never** label a model-generated idea as original or scientifically verified without independent, inspectable evidence.
- Keep scientific evidence, novelty assessment, measurement validity, execution permission and paper readiness as separate dimensions.
- Preserve explicit baselines, falsifiers, confounders and source assumptions on every idea.
- A dramatic headline is not evidence of a major discovery. Prefer decisive experiments and calibrated uncertainty.
- Retain negative outcomes and prior candidate lineage; do not rename killed ideas to evade review.
- No unattended expensive compute, external communications, submissions, provider spending, or credential mutations without authorization.
- Treat a RanchoResearch handoff as inert `PROPOSED_REVIEW`; follow its evidence-gate skill and RanchoControl worker protocol before creating an executable task.

## Engineering constraints
- Python 3.10+, standard-library runtime, minimal optional dependencies.
- Keep CLI, localhost UI and stable JSON schemas backward-compatible; version breaking changes.
- All stored user secrets must stay out of Git. Model keys are environment-only, never sent to the browser.
- For tests: `python -m unittest discover -s tests -v` and `nova roll --count 2 --seed 42`.
- Test model integrations with fake clients; tests must never need live paid API access.
- Use an isolated feature branch and PR for substantive changes unless user explicitly requests direct main writes.
