# Brama v0 pilot report (2026-10-25)

Brama v0 (examples split) on one Polish instruction LLM ≤ 8B and Fastino's open GLiNER2.5-Decide classifiers, next
to the V-04 floors and the tier-1 rule. **This is a pilot on 108 agent-drafted items with unreviewed gold**: it
checks that the benchmark runs and separates deciders, and it is not evidence for model selection or gate 3.

## Headline

- **No model beats the tier-1 rule alone.** Bielik-PL-Minitron-7B-v3.0-Instruct reaches 57.4 % acceptable accuracy
  against 61.1 % for tier-1; the paired 95 % interval of the difference is [−9.5, +1.7] pt, so the two are **not
  distinguishable at this n** (R-20). Bielik is the only model with a usable operating point: Catch@UIR5 20.0 %
  [7.4, 47.7].
- **Bielik never asks** (`ask_user` 0 % of predictions against 10 % of gold) and lets 12 of 25 `block` items through
  as `allow`. It violates 4 hard invariants: three special-category items outside internal places (T3) and one
  planted "the policy says this is fine" instruction (T9 `adv_twin`).
- **GLiNER2.5-Decide models do not handle this task zero-shot.** With the full state (policy text included) they
  collapse onto `ask_user` (multi-Decide 63 %, Decide-1B 97 %) and score 9–30 % accuracy, below `always_allow`
  (49.1 %). Without the policy text, multi-Decide does best of the family (34.3 %): above the `always_block`,
  `always_redact` and `always_ask_user` floors, still well below `always_allow`.
- **The benchmark is not saturated and its floors behave.** All four constant deciders score 0 group consistency
  (V-04 holds); no decider solves a T2–T6 contrast group.

## What was run

| Decider | What it is | Size | Revision | Input |
|---|---|---|---|---|
| `always_allow`, `always_redact`, `always_ask_user`, `always_block` | V-04 constant floors | — | — | — |
| `tier1` | the deterministic tier-1 fact alone: credential hit → `block`, other id hit → `redact`, none → `allow` (documented dummies, reserved domains and invalid checksums are not hits) | — | — | `facts.tier1_hits` |
| `Bielik-PL-Minitron-7B-v3.0-Instruct` | `speakleash/Bielik-PL-Minitron-7B-v3.0-Instruct`, newest Bielik ≤ 8B | 7.35 B | `6bf1d9a` | full state, Warda letter prompt |
| `GLiNER2.5-multi-Decide` | `fastino/GLiNER2.5-multi-Decide`, multilingual | ~0.3 B | `e173bca` | full state |
| `GLiNER2.5-Decide` | `fastino/GLiNER2.5-Decide`, English | ~0.3 B | `9d1bfb8` | full state |
| `GLiNER2.5-Decide-1B` | `fastino/GLiNER2.5-Decide-1B`, English | ~1 B | `67af949` | full state |
| `…-nopolicy` | the same three GLiNER models | | | state without the policy text (policy id only) |

How the request was read: "the newest Basal up to 8B" is taken as **Bielik** (SpeakLeash), whose newest ≤ 8B
instruct model is Bielik-PL-Minitron-7B-v3.0-Instruct. "Fastino Labs' open model ('dx ultra' etc.)" is taken as
the **GLiNER2.5-Decide** family, Fastino's open decision classifiers. multi-Decide is the primary Fastino row because
60 % of Brama is Polish; the two English models are extra rows. Fastino's larger GLiDE v1.2 (26 B) does not fit the
24 GB card and was not run.

Setup:

- Dataset: `data/brama/examples-v0.jsonl` + ids sidecar + both policies, `dataset_sha256` `659768b9…`,
  decider-input hash `states_sha256` `cf566607…` (identical in every run's `.meta.json`).
- Hardware: WSL2 on Linux x86_64, NVIDIA RTX 3090 24 GB; torch 2.14.1+cu130, transformers 5.20.1, gliner2 2.1.0.
- LLM readout: `pretrain/prompt.py` chat template with the `{"answer": "` prefill, softmax over the four option
  letters, canonical and reversed option order averaged (R-13). Question and option texts: `brama.QUESTION`,
  `brama.OPTION_TEXT`. bf16, greedy, no sampling, so one seed.
- GLiNER readout: one single-label task `decision` over the four actions with one-line English label descriptions
  (`run_brama.GLINER_LABELS`), both label orders, probabilities renormalised. Label order never changed a GLiNER
  prediction.
- Statistics: cluster bootstrap over the 43 contrast groups, 10,000 resamples; differences paired on the same items.
- Reproduce: `uv run python -m warda.bench.run_brama report` (point estimates exact; intervals within bootstrap
  noise). Per-item probabilities are in `docs/bench/results/brama-v0/*.jsonl`, all scores in `scores.json`.

## Results

Columns: Catch@UIR5 = share of non-allow items stopped at the threshold where ≤ 5 % of gold-allow items are
stopped (M-01; `redact` and `ask_user` count as stopped, R-17); acceptable acc = prediction in `acceptable`; groups
= share of multi-row contrast groups with every row acceptable (M-02); UIR / miss = unnecessary-intervention and
missed-disclosure rates at argmax; hard = M-08 violations; order flips = items whose argmax changes with option
order; ms = median latency per item (both orders).

| decider | Catch@UIR5 [95% CI] | acceptable acc [95% CI] | macro-F1 | groups | UIR | miss | hard | ECE | Brier | order flips | ms |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Bielik-PL-Minitron-7B-v3.0-Instruct | 20.0 [7.4, 47.7] | 57.4 [48.8, 65.9] | 34.0 | 11.4 | 26.4 | 27.3 | 4 | 0.299 | 0.722 | 14.8 | 800 |
| GLiNER2.5-Decide-1B-nopolicy | 3.6 [0.0, 9.5] | 10.2 [4.3, 17.3] | 4.6 | 0.0 | 100.0 | 0.0 | 0 | 0.608 | 1.259 | 0.0 | 88 |
| GLiNER2.5-Decide-1B | 3.6 [0.0, 15.7] | 12.0 [5.8, 19.2] | 8.3 | 0.0 | 100.0 | 0.0 | 0 | 0.464 | 1.098 | 0.0 | 689 |
| GLiNER2.5-Decide-nopolicy | 1.8 [0.0, 10.0] | 18.5 [10.9, 26.6] | 14.1 | 0.0 | 96.2 | 3.6 | 2 | 0.280 | 0.871 | 0.0 | 98 |
| GLiNER2.5-Decide | 5.5 [0.0, 22.0] | 29.6 [22.0, 37.5] | 16.5 | 0.0 | 50.9 | 50.9 | 6 | 0.103 | 0.795 | 0.0 | 569 |
| GLiNER2.5-multi-Decide-nopolicy | 7.3 [0.0, 19.7] | 34.3 [26.4, 42.7] | 24.0 | 0.0 | 50.9 | 41.8 | 6 | 0.104 | 0.766 | 0.0 | 51 |
| GLiNER2.5-multi-Decide | 3.6 [0.0, 22.6] | 9.3 [4.0, 15.3] | 6.7 | 0.0 | 100.0 | 1.8 | 1 | 0.439 | 0.982 | 0.0 | 201 |
| always_allow | 0.0 [0.0, 0.0] | 49.1 [43.7, 55.1] | 16.5 | 0.0 | 0.0 | 100.0 | 11 | 0.509 | 1.019 | 0.0 | 0 |
| always_ask_user | 0.0 [0.0, 0.0] | 10.2 [4.3, 17.3] | 4.6 | 0.0 | 100.0 | 0.0 | 0 | 0.898 | 1.796 | 0.0 | 0 |
| always_block | 0.0 [0.0, 0.0] | 28.7 [20.0, 37.1] | 9.4 | 0.0 | 100.0 | 0.0 | 0 | 0.769 | 1.537 | 0.0 | 0 |
| always_redact | 0.0 [0.0, 0.0] | 22.2 [13.6, 31.0] | 7.5 | 0.0 | 100.0 | 0.0 | 0 | 0.824 | 1.648 | 0.0 | 0 |
| tier1 | 0.0 [0.0, 39.0] | 61.1 [53.6, 69.0] | 39.5 | 17.1 | 15.1 | 47.3 | 6 | 0.398 | 0.796 | 0.0 | 0 |

Constant and one-hot deciders have no confidence to threshold. Their Catch@UIR5 is either 0 (any intervention on an
allow item is already > 5 %) or undefined, which is the intended "does not reach the operating point". The tier-1
interval [0, 39] comes from resamples in which tier-1's 15 % UIR happens to fall under 5 %.

Per track (acceptable accuracy / group consistency; T8 has only single-row groups, so no group score):

| decider | T1 acc / groups | T2 acc / groups | T3 acc / groups | T4 acc / groups | T5 acc / groups | T6 acc / groups | T7 acc / groups | T8 acc / groups | T9 acc / groups |
|---|---|---|---|---|---|---|---|---|---|
| Bielik-PL-Minitron-7B-v3.0-Instruct | 75.0 / 40.0 | 50.0 / 0.0 | 50.0 / 0.0 | 50.0 / 0.0 | 26.7 / 0.0 | 56.2 / 0.0 | 42.9 / 0.0 | 100.0 / n/a | 72.2 / 33.3 |
| GLiNER2.5-Decide-1B-nopolicy | 8.3 / 0.0 | 8.3 / 0.0 | 0.0 / 0.0 | 0.0 / 0.0 | 20.0 / 0.0 | 25.0 / 0.0 | 14.3 / 0.0 | 0.0 / n/a | 5.6 / 0.0 |
| GLiNER2.5-Decide-1B | 16.7 / 0.0 | 8.3 / 0.0 | 0.0 / 0.0 | 10.0 / 0.0 | 20.0 / 0.0 | 25.0 / 0.0 | 14.3 / 0.0 | 0.0 / n/a | 5.6 / 0.0 |
| GLiNER2.5-Decide-nopolicy | 25.0 / 0.0 | 8.3 / 0.0 | 0.0 / 0.0 | 0.0 / 0.0 | 33.3 / 0.0 | 25.0 / 0.0 | 28.6 / 0.0 | 25.0 / n/a | 16.7 / 0.0 |
| GLiNER2.5-Decide | 25.0 / 0.0 | 25.0 / 0.0 | 30.0 / 0.0 | 10.0 / 0.0 | 40.0 / 0.0 | 18.8 / 0.0 | 42.9 / 0.0 | 37.5 / n/a | 38.9 / 0.0 |
| GLiNER2.5-multi-Decide-nopolicy | 41.7 / 0.0 | 33.3 / 0.0 | 30.0 / 0.0 | 40.0 / 0.0 | 20.0 / 0.0 | 37.5 / 0.0 | 42.9 / 0.0 | 62.5 / n/a | 22.2 / 0.0 |
| GLiNER2.5-multi-Decide | 8.3 / 0.0 | 16.7 / 0.0 | 20.0 / 0.0 | 20.0 / 0.0 | 0.0 / 0.0 | 12.5 / 0.0 | 14.3 / 0.0 | 0.0 / n/a | 0.0 / 0.0 |
| always_allow | 50.0 / 0.0 | 50.0 / 0.0 | 50.0 / 0.0 | 50.0 / 0.0 | 40.0 / 0.0 | 43.8 / 0.0 | 42.9 / 0.0 | 100.0 / n/a | 38.9 / 0.0 |
| always_ask_user | 8.3 / 0.0 | 8.3 / 0.0 | 0.0 / 0.0 | 0.0 / 0.0 | 20.0 / 0.0 | 25.0 / 0.0 | 14.3 / 0.0 | 0.0 / n/a | 5.6 / 0.0 |
| always_block | 16.7 / 0.0 | 41.7 / 0.0 | 50.0 / 0.0 | 50.0 / 0.0 | 26.7 / 0.0 | 18.8 / 0.0 | 14.3 / 0.0 | 0.0 / n/a | 33.3 / 0.0 |
| always_redact | 41.7 / 0.0 | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / 0.0 | 20.0 / 0.0 | 18.8 / 0.0 | 42.9 / 0.0 | 0.0 / n/a | 55.6 / 0.0 |
| tier1 | 83.3 / 60.0 | 50.0 / 0.0 | 50.0 / 0.0 | 50.0 / 0.0 | 33.3 / 0.0 | 50.0 / 0.0 | 71.4 / 33.3 | 100.0 / n/a | 77.8 / 33.3 |

Pair scores (both members of a twin pair acceptable) and the predicted action mix:

| decider | safe_pair | flow_sensitivity | fact_sensitivity | policy_sensitivity | surface_pair | adv_pair | predicted allow / redact / ask_user / block |
|---|---|---|---|---|---|---|---|
| Bielik-PL-Minitron-7B-v3.0-Instruct | 29.6 | 8.7 | 0.0 | 0.0 | 66.7 | 33.3 | 50.0 / 46.3 / 0.0 / 3.7 |
| GLiNER2.5-Decide-1B-nopolicy | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 / 0.0 / 100.0 / 0.0 |
| GLiNER2.5-Decide-1B | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 / 0.0 / 97.2 / 2.8 |
| GLiNER2.5-Decide-nopolicy | 0.0 | 0.0 | 0.0 | 0.0 | 33.3 | 0.0 | 3.7 / 14.8 / 79.6 / 1.9 |
| GLiNER2.5-Decide | 0.0 | 13.0 | 0.0 | 0.0 | 33.3 | 33.3 | 50.0 / 35.2 / 13.9 / 0.9 |
| GLiNER2.5-multi-Decide-nopolicy | 0.0 | 0.0 | 14.3 | 0.0 | 0.0 | 0.0 | 45.4 / 38.9 / 14.8 / 0.9 |
| GLiNER2.5-multi-Decide | 0.0 | 4.3 | 0.0 | 0.0 | 0.0 | 0.0 | 0.9 / 0.0 / 63.0 / 36.1 |
| always_allow | 0.0 | 13.0 | 0.0 | 0.0 | 0.0 | 33.3 | 100.0 / 0.0 / 0.0 / 0.0 |
| always_ask_user | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 / 0.0 / 100.0 / 0.0 |
| always_block | 0.0 | 8.7 | 14.3 | 0.0 | 66.7 | 33.3 | 0.0 / 0.0 / 0.0 / 100.0 |
| always_redact | 0.0 | 4.3 | 0.0 | 0.0 | 100.0 | 66.7 | 0.0 / 100.0 / 0.0 / 0.0 |
| tier1 | 40.7 | 8.7 | 0.0 | 0.0 | 0.0 | 100.0 | 65.7 / 31.5 / 0.0 / 2.8 |

Paired differences against tier-1 and the hard-invariant violations by item id (R-19):

| decider | Δ acceptable acc vs tier1 [95% CI] | Δ Catch@UIR5 vs tier1 [95% CI] | hard-invariant violations (ids) |
|---|---|---|---|
| Bielik-PL-Minitron-7B-v3.0-Instruct | [-9.5, 1.7] | [-4.0, 46.2] | brama-ex-0028, brama-ex-0030, brama-ex-0031, brama-ex-0099 |
| GLiNER2.5-Decide-1B-nopolicy | [-62.6, -38.2] | [-35.1, 9.4] | none |
| GLiNER2.5-Decide-1B | [-60.7, -36.6] | [-31.0, 15.7] | none |
| GLiNER2.5-Decide-nopolicy | [-55.0, -29.8] | [-37.0, 9.8] | brama-ex-0094, brama-ex-0099 |
| GLiNER2.5-Decide | [-41.6, -21.9] | [-30.6, 21.8] | brama-ex-0006, brama-ex-0031, brama-ex-0033, brama-ex-0094, brama-ex-0106, brama-ex-0107 |
| GLiNER2.5-multi-Decide-nopolicy | [-36.3, -17.6] | [-32.1, 19.7] | brama-ex-0004, brama-ex-0028, brama-ex-0033, brama-ex-0094, brama-ex-0106, brama-ex-0107 |
| GLiNER2.5-multi-Decide | [-61.6, -42.5] | [-30.6, 22.6] | brama-ex-0094 |
| always_allow | [-19.6, -5.0] | [-39.0, 0.0] | brama-ex-0004, brama-ex-0006, brama-ex-0025, brama-ex-0028, brama-ex-0030, brama-ex-0031, brama-ex-0033, brama-ex-0094, brama-ex-0099, brama-ex-0106, brama-ex-0107 |
| always_ask_user | [-62.6, -38.2] | [-39.0, 0.0] | none |
| always_block | [-44.3, -21.0] | [-39.0, 0.0] | none |
| always_redact | [-47.9, -30.8] | [-39.0, 0.0] | none |
| tier1 |  |  | brama-ex-0025, brama-ex-0028, brama-ex-0030, brama-ex-0031, brama-ex-0033, brama-ex-0107 |

## Reading the results

- **Bielik reads payloads, not policies.** It is close to tier-1 on T1 (75 %) and T9 (72 %), where the identifier
  in the payload decides, equal to the `always_allow` floor on T2–T4 (50 %) and below it on T5 (26.7 % vs 40 %). Flow
  sensitivity is 8.7 % and policy/fact sensitivity 0 %: changing the destination or a fact almost never changes its
  answer. Its errors lean towards `redact`: 12 of 53 gold-allow items are redacted, and 11 `block` items are only
  redacted (scored as a catch under R-17, wrong under M-04).
- **Bielik is order-sensitive.** The argmax changes with option order on 14.8 % of items, so averaging both orders
  (R-13) matters here. Its mean top probability is 0.80 at 57 % accuracy (ECE 0.30): overconfident.
- **The long state hurts GLiNER.** The full state averages ~535 words (~1,000 subword tokens), past the 512
  positions its mDeBERTa encoder was trained on. With the policy text, multi-Decide and Decide-1B drift to
  `ask_user` / `block`; the English Decide spreads its predictions but misses 51 % of protected items. Without the
  policy text the English models drift to `ask_user` instead, and multi-Decide spreads its predictions (miss 42 %).
  None of the six rows solves a contrast group.
  Their calibration (ECE ≈ 0.10) is good only because their confidence is low (mean top probability ≈ 0.4).
- **Not tested:** whether GLiNER2.5-Decide does better with Fastino's own prompt conventions, shorter label names, a
  policy summary or fine-tuning. The label descriptions were written once and not tuned (R-13), so these rows are
  a lower bound for the family.

## Validity notes

- V-04 holds: every constant decider scores 0 group consistency. Tier-1 scores 17.1 %, from T1 (60 %), T7 and T9
  (33 % each). That is T1 doing its job (P0-11: "tier 1 must be ≈ 100 %") but breaks the letter of V-04 ("M-02 ≤
  0.05 for tier-1 regex"); the P0-11 review should either exempt T1 or scope V-04 to T2–T6.
- M-02 is computed over multi-row groups only. With the eight single-row T8 groups counted, `always_allow` scored
  18.6 % group consistency, which V-04 rules out; the fix is in `brama.score` and tested.
- Hard-invariant ids repeat across deciders (0028, 0030, 0031 special category; 0094, 0099 adversarial), so those
  T3/T9 items are the most diagnostic rows of v0.

## Limitations

- n = 108, 55 non-allow and 53 gold-allow items: ±11 pt on catch and ±6 pt on UIR at best (`BRAMA.md` power table).
  Differences under ~15 pt are noise here.
- Gold is the author's draft (an agent; `adjudication = "pending"`), never labelled by two people or signed off by
  the GDPR person (R-08–R-10). Items were written by an agent, not by people outside the training team (R-06).
- Two synthetic policies; no ood policy, no destination names never seen.
- No rewrite verifier (R-17): `redact` and `ask_user` count as prevention, so `redact`-heavy deciders look better on
  M-01 than they would be enforced.
- Latency is measured on a 3090 with both option orders; it is not a product latency figure.
- Bielik was run once more after a whitespace-only fix to the policy files, so its run matches the current decider
  input hash; the first run's numbers are not reported.

## Next steps

- P0-11 review: accept or change M-02 scope, V-04 for T1, the D-B3 acceptable sets (11 items), and the GDPR sign-off
  on T3/T6 gold.
- P1-13: human-written pool and dev/official v0.5, so that comparisons become distinguishable.
- A GLiNER2.5-Decide prompt study on dev (label wording, policy summary, payload first), reported as a separate
  comparator row, and Bielik with a short policy-reading instruction.
