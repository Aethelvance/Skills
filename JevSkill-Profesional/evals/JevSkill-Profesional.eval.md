# Eval: jevskill-profesional-skill

Regression spec. Run the golden inputs through `scripts/jev_call.py --mock` and
check the binary criteria below. Golden cases are input-only; the mock gives
deterministic fakes so the harness tests wiring, validation, and gating — not
Jev's judgement. Live judgement is verified by inspection, never asserted here.

## Criteria (all must pass, `command` graded)

1. `mock-label`: verdict `source == "mock"` and `model == "mock"` and
   `usage.input_tokens == 0`. A mock must never pass as Jev.
2. `typed-or-error`: malformed answers (missing answer, wrong type, non-finite)
   exit `2` with no invented verdict. Run `scripts/jev_call.py` against
   `evals/golden/tax-kind/bad-answers.json` questions to check.
3. `gate-floor`: an answer with `confidence < --min-confidence` writes
   `gated: false` with a `reason`, exit `0`. Never acts on it.
4. `choice-closed`: a `choice` outside `criteria` exits `2`.
5. `latency-usage-present`: every written verdict carries `latency_ms` and `usage`.

## Golden cases

| Case | Input | What it proves |
| --- | --- | --- |
| `curate-reject` | circular reasoning trace | `noul` + `score` fan-out wires and validates |
| `killmyidea-score` | startup idea + goal | multi-`score` + `choice` + `noul` in one POST |
| `tax-kind` | page header/body/footer | `choice` with `not_in_this_list` coverage |

```bash
python3 scripts/jev_call.py --mock --state evals/golden/curate-reject/state.json --questions evals/golden/curate-reject/questions.json --out /tmp/curate.json
python3 scripts/jev_call.py --mock --state evals/golden/killmyidea-score/state.json --questions evals/golden/killmyidea-score/questions.json --out /tmp/kill.json
python3 scripts/jev_call.py --mock --state evals/golden/tax-kind/state.json --questions evals/golden/tax-kind/questions.json --out /tmp/tax.json
```
