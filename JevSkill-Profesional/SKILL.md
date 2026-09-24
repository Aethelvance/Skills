---
name: JevSkill-Profesional
description: >-
  Judge with Jev System One (TypeSafe): typed noul/score/choice verdicts over a
  structured state in one round-trip. Use when the user needs programmable
  judgement: routing, ranking, extraction, verification, classification,
  scoring, or gating. Triggers on "judge with Jev", "classify / score /
  verify this", "route / rank / extract / verify with Jev", or any task that
  needs a calibrated probability instead of generated prose. Does not generate
  text, run workflows, or touch actuators; code owns execution.
license: MIT
activation: /JevSkill-Profesional
metadata:
  author: Aethelvance
  version: 1.0.0
  created: 2026-09-24
  last_reviewed: 2026-09-24
  review_interval_days: 90
  dependencies:
    - name: TypeSafe System One API
      url: https://api.typesafe.ai/v1/systemone
      type: service
provenance:
  maintainer: Aethelvance
  version: 1.0.0
  created: 2026-09-24
  source_references:
    - https://docs.typesafe.ai/llms.txt
compatibility: >-
  Any agent that can POST HTTPS + read SKILL.md. Key stays server-side;
  no browser, pixel, or actuator access required.
---

# /JevSkill-Profesional

Turn a decision into typed Jev judgements. Code owns the workflow; Jev supplies
one round of calibrated `noul / score / choice` answers over a structured `state`.

## Run

```bash
export TYPESAFE_API_KEY=...  # never commit, never log, never send to browser
python3 scripts/jev_call.py --state state.json --questions questions.json --out verdict.json
```

The script does one `POST`, validates the typed answers, applies the confidence
gate, and exits non-zero instead of inventing a verdict. Run `python3 scripts/jev_call.py --help`
for flags (`--model`, `--timeout-ms`, `--min-confidence`).

## Verify

Run `python3 scripts/run_evals.py` — the skill's built-in evaluator (stdlib
only, no key needed for the 19 offline checks; with `TYPESAFE_API_KEY` it also
runs the 8 live claim checks). Exit 0 means the skill is coherent and true.

## Required behavior

1. Put everything Jev needs in `state`. Structured data, never pixels or hidden
   client context. If the state lacks it, the option is uninferable by design.
2. Ask one narrow judgement per question. `instructions` carries the question,
   `criteria` defines the answers. Keep it in one `POST` (fan-out); a second
   request only when an earlier answer fetches new evidence or options.
3. Read the typed answer or fail. Missing answer, wrong type, or non-finite
   number is `502` — never a filled-in verdict.
4. Gate on confidence. Default `confidence < 0.5` means skip/reject, not act.
   The final confidence is the minimum of the axes used.
5. Let code execute. Jev returns a label or level; thresholds, prices, timing,
   and safety vetoes live in code. No answer touches an actuator directly.
6. Label the source. `jev` real, `mock` simulated, `error:<Type>` failed.
   Simulated and live never share a label or a cost figure.
7. Expose `latency_ms`, `usage.input_tokens`, and probabilities on every verdict.

## Gotchas

- `jev-latest` currently resolves to `jev-1.13.0`. Pin only if you must reproduce
  a benchmark; otherwise request `jev-latest`.
- A `noul` near `0.5` means similar probability for yes/no, not medium intensity.
  A low `choice/score` confidence can mean several good options, not a bad read.
- `score` saturates ("clearly better" on every child when winning). Rank with a
  code-computed delta, not with raw scores alone.
- `429/529` means back off and honor `retry-after` (or `retry-after-ms`); any
  other 4xx is not retryable. Rate limit is `20 req/s`.
- Late is skip. A judgement that arrives after its window is discarded and
  counted, never applied retroactively.
- `choice` confidence ≈1.0 does not mean a clear case: genuine 3-way ties also
  one-hot at ~1.0. Below ~0.5 it reliably flags bad fit → reject; near 1.0 on
  high-stakes close calls → verify with per-option nouls first.
- `score` is an index 0..n-1 into YOUR criteria, not 0-4 fixed. Normalize as
  `score / (levels-1) × 100`.
- The request envelope is strict: exactly `{model, state, questions}`, all
  required, no extra keys (extras → 400). Always send an OBJECT state.

## References

Read on demand, one file per need — do not load all upfront:

- Read `references/transport.md` when wiring the HTTP call, SDK, or mock.
- Read `references/primitives.md` when writing `state`, `instructions`, `criteria`.
- Read `references/composition.md` when batching, fanning out, or budgeting calls.
- Read `references/verdict.md` when setting thresholds, weights, or gates.
- Read `references/reliability.md` when handling timeouts, retries, cache, late/stale.
- Read `references/security.md` when handling keys, simulators, or fallbacks.
- Read `references/patterns.md` when choosing route / select / evidence / scoring / verify / reactive.
- Read `references/calibration.md` before trusting a number (noul honest, score
  = weighted index, choice = winner-takes-all).
- Read `references/errors.md` when a call fails (observed status table + retry rules).
