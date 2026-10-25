+++
id = "P0-12"
title = "Brama v0: example set, validator, pilot runner and first pilot report"
labels = ["phase:0", "team:benchmarks", "type:feature", "gate:3"]
milestone = "Phase 0 — Kick-off (weeks 1–2)"
depends_on = ["P0-11"]
estimate_hours = 8
hardware = "strong"
github_issue = 0
+++

## Context

P0-11 designs the Brama benchmark and asks for an example file with ≥ 3 contrast groups per track, two example
policies, a validator and a leakage test (R-12). Nothing yet shows that the design can be run end to end, or how
far existing small open models are from the trivial floors. This task builds the v0 examples split from the
P0-11 proposal (read via the plain-language summary `docs/issues/pl/P0-11-brama-benchmark-design_PROSTO.md`), adds
the runner, and pilots it on one Polish instruction LLM ≤ 8B and on Fastino's open GLiNER2.5-Decide classifiers.

## Scope

- In: the examples split (fictional only), both example policies, the identifier sidecar, validator, decider view,
  metrics with cluster bootstrap, a runner for constant, tier-1, Hugging Face causal LM and GLiNER2 deciders, a
  pilot report.
- Out: dev / official splits (P1-13), human labels and adjudication (P0-04/P0-05), the rewrite verifier (R-17), the
  P0-06 shared runner (v0 has its own until P0-06 lands), API models.

## Deliverables

- `data/brama/examples-v0.jsonl`, `data/brama/examples-v0.ids.json`, `data/brama/policies/*.md`,
  `data/brama/CARD.md`.
- `warda/bench/brama.py`, `warda/bench/run_brama.py`, `warda/bench/tests/test_brama_examples.py`.
- `docs/bench/BRAMA.md` (v0 record against P0-11), `docs/bench/results/brama-v0/`,
  `docs/bench/reports/brama-v0-pilot-2026-10-25.md`.
- `docs/decisions/ADR-draft-brama-open-decisions.md`; follow-up `docs/issues/P1-13-brama-dev-and-official-v05.md`.

## Definition of done

- [ ] ≥ 3 groups per track T1–T9, both policies used, PL/EN within 60/40 ± 10, every row validates
- [ ] R-12 test passes: hidden fields never change the rendered decider state
- [ ] Pilot report covers the floors (V-04), tier-1, one Bielik ≤ 8B and the GLiNER2.5-Decide models, with CIs
- [ ] Every run records model revision, dataset hash and hardware
- [ ] The GDPR person has reviewed the T3 and T6 gold, or the report states that gold is unreviewed

## Automated tests

- `warda/bench/tests/test_brama_examples.py`: schema and enums, twin structure, balance (R-07), `protected` in the
  payload (R-11), hard invariants on gold (M-08), canary, sidecar reproducibility and checksums, clause existence,
  R-12 leakage, metric sanity (gold scores perfect, Catch@UIR budget, bootstrap).

## Documentation

- `docs/bench/BRAMA.md`, `data/brama/CARD.md`, the pilot report; `README.md` Contents and `AGENTS.md` (commands,
  layout, Brama item format).

## Manual test (human, before the PR)

1. `uv run python -m warda.bench.run_brama report --resamples 1000` reproduces the table in the pilot report within
   bootstrap noise (point estimates exactly).
2. Read three groups (one each from T2, T5, T9) and name the minimal edit between base and each twin (R-04).
3. Search the example file and sidecar for your employer's name, real colleagues' names and real identifiers → zero
   hits.
