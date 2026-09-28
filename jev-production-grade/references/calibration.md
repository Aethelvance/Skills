# Calibration

How the three primitives actually behave, measured live over 50+ probes
(`Skill/tests/experimental/`). Read this before trusting a number.

## noul: an honest probability

- Extremes hit `0.99` / `0.01` where deserved; genuine semantic uncertainty
  sits mid-range (`0.49`); clear negatives report low (`0.03`, `0.08`).
- noul answers carry NO confidence field — there is nothing missing, the
  number IS the uncertainty. Our `min_confidence` treats absent as 1.0.
- Rule: read noul at face value against your threshold. Near 0.5 = tie.

## score: weighted index + concentration confidence

- `score = Σ index × P(index)` over YOUR criteria (verified: levels
  `[0..4]` with probs `{1:0.1, 2:0.89, 3:0.01}` → `1.91`).
- Confidence tracks DISTRIBUTION CONCENTRATION, not correctness: 0.89 mass on
  one level → 0.91 confidence, even for a mediocre input. Floor hits (`0.02`)
  also report ~0.99. A `legend` echoing your criteria is included.
- Rule: normalize as `score / (levels-1) × 100`. Expect high confidence
  whenever mass concentrates — it does not mean "good", it means "decided".

## choice: winner-takes-all, confidence = winner fit

- When Jev LOCKS onto a reading it one-hots (`{winner: 1.0}`) with confidence
  ~1.0 — even on genuine 3-way overlap with no lexical cue (replicated).
  Clear cases look identical. Choice confidence CANNOT separate "obvious"
  from "contested".
- When LOST it doubts honestly: pure noise → {0.52, 0.48} + confidence 0.04;
  total mismatch → spread + 0.22. Twin options are discriminated exactly.
- Without an escape hatch a no-match is force-picked at low confidence; with a
  `not_in_this_list`/`neither` option the hatch catches it at 1.0.
- Rules:
  1. `confidence < 0.5` → reject/ask. It reliably flags bad fit.
  2. `~1.0` on high-stakes close calls → verify with per-option nouls first.
  3. Always ship the escape option. Probabilities are meaningless for audit
     when one-hot — the audit trail is the winning label plus your gate.
  4. For contested multi-label calls prefer N nouls (one per candidate, each
     independently calibrated) over 1 choice.
