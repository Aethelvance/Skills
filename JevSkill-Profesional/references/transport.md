# Transport

How `state + questions` reaches Jev and returns typed. Use this when wiring the
HTTP call, picking an SDK, or building a mock. The rest of the skill assumes
this contract.

## Endpoint and auth

- `POST https://api.typesafe.ai/v1/systemone`
- Headers: `Authorization: Bearer <TYPESAFE_API_KEY>`, `Content-Type: application/json`
- The key lives server-side / in memory only (`process.env` / `os.environ`). Never
  in the browser, on disk, in logs, or in a repo. Without a key there is no live
  mode: start degraded.
- Local mock: same body against your own `--endpoint` / `TYPESAFE_ENDPOINT`, or
  `TYPESAFE_MOCK=1` with responses labelled `model: "mock"`.

## Model

- Request `model: "jev-latest"`. It currently resolves to `jev-1.13.0`; pin
  `jev-1.13.0` only to reproduce a benchmark.
- Observed SDKs (equivalent, pick one):
  - JS: `import { TypeSafeClient } from "@typesafe-ai/sdk"` →
    `client.systemOne({ state, questions })`, `new TypeSafeClient({ timeout })`
  - Python: `from typesafe_sdk import TypeSafeClient, Choice, Noul, Score`
  - AI SDK: `typeSafeAi.evaluationModel("jev-latest")` + `experimental_evaluate(...)`
  - Direct: `httpx` / `fetch` with the body below (ultrafast, tax, pg do this).

## Body and response

```json
{
  "model": "jev-latest",
  "state": {"text": "...", "rows": [...]},
  "questions": {
    "is_bad": {"type": "noul", "instructions": "...", "criteria": {"true": "...", "false": "..."}},
    "quality": {"type": "score", "instructions": "...", "criteria": ["level 0", "level 1", "level 2", "level 3", "level 4"]},
    "route": {"type": "choice", "instructions": "...", "criteria": {"a": "...", "b": "..."}}
  }
}
```

```json
{"answers": {"is_bad": {"noul": 0.05}, "quality": {"score": 3.2, "confidence": 0.9}}, "usage": {"input_tokens": 1234, "output_tokens": 0}}
```

Every field of each answer is optional in the type: your code must require it.
`usage.input_tokens` feeds cost (`× 0.042 / 1M`, output free).

The envelope is STRICT (measured): exactly `{model, state, questions}`, all
required, zero extra keys — extras → 400, missing → 422. See `errors.md`.

## Timing and rate

- Timeout with real abort per call (2s interactive, 12s batch, 30-90s bulk).
  Without a timeout a slow decision blocks the next one.
- Limit: `20 req/s` (`1200 req/min`). On `429/529` honor `retry-after`
  (or `retry-after-ms`), wait capped at ~30s. Any other 4xx is not retryable.
  Measured: short bursts to ~31 rps never tripped a 429 — the binding budget is
  per-minute, not per-second. Pace sustained loads anyway.
- Retry with backoff + jitter (`0.5s ×2` capped at `8s`, 1-4 attempts by
  criticality; `maxRetries: 0` when late means skip and the slot stays empty).
- Always measure and expose the full round-trip `latency_ms`, retries included.
