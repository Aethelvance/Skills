# Errors

Every status below was observed live. The envelope is fully strict:
`{model, state, questions}` are all required and no extra keys are accepted.
Map once, handle forever — never invent a verdict on any of these.

| Status | When | Body detail | Client action |
| --- | --- | --- | --- |
| 401 | Wrong key | `authentication_error` | Fix key, do not retry as-is |
| 403 | Empty/missing key | `authentication_error: Must supply an API key!` | Configure key, start degraded meanwhile |
| 400 | Unknown model | `api_usage_error: Unknown model: ...` | Pin `jev-latest` / `jev-1.13.0` |
| 400 | Extra top-level field | strict-body rejection | Send exactly `{model, state, questions}` |
| 400 | Empty choice criteria | `Choice question must have at least one choice` | Build criteria before sending |
| 400 | Oversize state | `max_tokens_exceeded` | Chunk state (50k chars passed; 200k failed) |
| 422 | Empty questions `{}` | `too_short`, min 1 item | Always ask ≥1 question |
| 422 | Malformed JSON | `json_invalid` | Fix serialization |
| 422 | Missing `type` | `union_tag_not_found`, discriminator `type` | Every question needs its type |
| 422 | Missing field | `Field required` (`model`/`state`) | Fill the envelope |
| 422 | Wrong state scalar | `state` must be `str \| dict \| list` (number rejected) | Send an OBJECT state (str/list answer ungrounded) |
| 429/529 | Over budget | honor `retry-after` / `retry-after-ms` | Back off; never observed in bursts ≤50 calls / ~31 rps |

Retry ONLY `408/429/529/≥500`. Everything in the 400/401/403/422 rows is final:
retrying them burns nothing but time — fix the request instead.
`scripts/jev_call.py` already implements exactly this split (exit 2, no verdict).
