# Verdict

How to go from answers to a decision. The verdict lives in code, never in model
prose.

## Typed read or error

- `readScore` requires `type: score` + a finite number; `readChoice` checks
  `choice` is in the list (unknown → `Other` or error by domain); `readNoul`
  requires a finite `type: noul`.
- Malformed response, missing answer, or missing field → `502`, never a
  filled-in verdict. Filter probabilities to `criteria` keys and renormalize;
  if they sum to ≤ 0, use uniform or error by criticality.

## Confidence gate

- Default: `confidence < 0.5` on any used answer → skip/reject, do not act.
  The final confidence is the **minimum** of the axes used: the weakest link rules.
- `noul ≈ 0.5` is a yes/no tie, not medium intensity. Low `choice` confidence
  with several good options is calibration, not indecision: it does not invalidate
  a harmless preference.
- Choice confidence measures WINNER FIT, not contest (see `calibration.md`):
  `< 0.5` reliably flags bad fit → reject; `~1.0` on high-stakes close calls →
  verify with per-option nouls before acting, because contested locks also read ~1.0.
- For contested multi-label calls prefer N nouls (one per candidate, each
  independently calibrated) over 1 choice; reserve choice for decisive routing.
- Domain gates on top of the base: clarity (`understandable < 0.3` asks for more
  detail instead of scoring), strict gate (`formConfidence >= 0.95` to archive),
  geometry veto (short requested for wide/grouped → code upgrades to long).
  Document every gate with its threshold and version.

## Weights and thresholds

- Normalize (`score / (levels-1) × 100` — with the conventional 5 levels that is
  `×25`) and take an explicit versioned weighted
  average (`SCORING_VERSION` bumps on any change to questions, weights, or
  thresholds). E.g. idea-killing dimensions ×2, rest ×1, total 10.
- Verdict by explicit bands. E.g. `KILL < 50 · FIX 50-64 · SHIP 65+`;
  `noul >= threshold` (argument > config > `0.5`); `capped` only forces the
  reducing side, never invents one; with no allowed side there is no quote
  (`NO QUOTE`).
- Keep the raw call in `probabilities` even when the cap corrects it, to audit
  requested vs executed.
