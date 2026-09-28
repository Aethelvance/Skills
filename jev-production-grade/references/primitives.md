# Primitives

What to ask and how to write it. Choose by what the answer means, not by its
shape.

| Need | Primitive | Distinction that matters |
| --- | --- | --- |
| One of a defined set | `choice` | Its distribution compares options against each other |
| Whether a condition holds | `noul` | Probability of yes; no separate confidence; one per label when several apply |
| Degree along an ordered dimension | `score` | Index 0..n-1 into your criteria, probability-weighted; use comparable per-item Scores for graded ranking |

## `state`: everything needed, nothing hidden

- Structured and bounded, never pixels or client-hidden context. If the state
  does not carry it, the option is uninferable and Jev is right not to pick it.
- Always send an OBJECT state with named fields. The API also accepts `str` and
  `list` states by type, but questions referencing `` `field` `` then match
  nothing and the answer is ungrounded (measured live).
- Name fields (`{"text": ...}`, `{"condition": ..., "rows": [...]}`) when there
  are several parts. Reference paths with backticks (`` `rows[0]` ``, `` `startup_idea` ``).
- Relative and readable (bps, `imbalance -1..1`, `"price x size"`), not absolutes
  tied to one regime. Include physical caps when they exist (ceiling, climb cap).
- Exact facts in code, not in the prompt: legal moves, captures, checks,
  balances, `header/body/footer` trimmed (e.g. body to 2500 chars). Whatever the
  code can compute belongs in code.

## `instructions` + `criteria`

- One question = one narrow, coherent judgement. Split independently useful
  dimensions without breaking the relationship being judged.
- `instructions` asks with complete meaning (IDs never reach the model).
  `criteria` defines each answer in one closed line that always means the same.
- `noul`: `criteria = {"true": "<what yes means>", "false": "<what no means>"}`.
  E.g. `true: "Contains circular derivations"` / `false: "Rigorous step-by-step reasoning"`.
- `score`: ordered list of levels, each a complete concrete situation, not
  adjectives (5 is the convention, but 2–10+ work — the answer is the
  probability-weighted INDEX 0..n-1, verified live). E.g. `0: "Broken, unrunnable"` … `4: "Production-grade, fully typed"`.
- `choice`: map `option -> one-line definition` plus `not_in_this_list` when
  nothing may fit — the hatch catches no-matches at 1.0, without it they are
  force-picked at low confidence (both measured live). Zero free text in the
  answer: only a listed `choice`. See `calibration.md` before trusting choice
  confidence.
- Include a no-match outcome and a separate presence judgement when useful. Check
  candidate coverage: the model cannot pick an omitted value.
