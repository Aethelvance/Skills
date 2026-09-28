# Reliability

How not to crash, not to block, and not to lie when something fails.

## Time and abort

- Every call carries a timeout with real abort (`AbortController` /
  `AbortSignal.timeout`) and in-flight calls can be cancelled.
- Every tick/block has a fixed cadence; a slow decision never blocks the next
  one. A single loop in flight: if the previous one is still running, the new
  one is marked `late` and neither decides nor quotes.
- Late is skip: a `pending` plan reaching its threshold is aborted
  (`late`, `skipped+=1`, `Decision arrived too late; no fallback used`).
  Never a ghost action or a retry faking punctuality.

## Retry and typed errors

- Retry only `408/429/529/≥500`, honoring `retry-after-ms` (else `Retry-After`)
  with a capped wait (~30s) + backoff with jitter.
- Map the rest: no key → `503/unconfigured`; exhausted `429/529` → `429/503
  Jev is busy`; timeout → `504 retryable:true`; rest → `502`; off-list `choice`
  → `502 invalid_typesafe_response retryable:true`.
- Workers never touch the host runtime directly; only the main thread emits
  errors and notices. Errors are counted without killing the session.

## Freshness, cache, and network budget

- Judgements expire: every reading carries an age and past the threshold it is
  ignored. Hold a commitment a few cycles to avoid oscillation, unless risk
  forces an immediate re-decision.
- Cache by content (`[type, query, kind, options]` + `sha1(row)`): hits never
  touch the API. Re-running or changing a threshold is free by design.
- Keep-alive connections per `(scheme, host, port)` capped at concurrency;
  cancellable waits in slices (e.g. 250ms) so timeouts and cancels get in.

## Mock and dry-run

- `TYPESAFE_MOCK=1` or `MODEL=mock` returns deterministic fakes with
  `model: "mock"`, `usage 0/0`, labelled `MOCK DATA (not Jev)`.
- Dry-run: `status: "sim"`, `txHash: null`, cost 0, fills `simulated: true`.
  Tests are 100% offline with mocks; live work with cost lives in `scripts/`,
  outside pytest.

## Size guidance

- 50k-char states answer fine; 200k chars → `400 max_tokens_exceeded`. The
  ceiling is token-based: budget ~12k input tokens per call and chunk above it.
  `usage.input_tokens` reports the real cost after each call.
