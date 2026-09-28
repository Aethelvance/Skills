# Security

Jev decides over data; code decides over the world. This split is what makes
the skill safe to operate.

## The model proposes, code disposes

- No answer touches actuators directly. Every action passes through a local
  translation that can refuse (bitmask, proximity threshold, climb veto,
  post-only price, signature and nonce).
- A safety layer always vetoes, whatever the answer says: hard reflex by
  distance/time-to-contact, ceiling verified with sensors, `allows_mate`
  excluding the move, cap that only reduces.
- Whatever the model cannot measure, code verifies with sensors, not with
  confidence.

## Secrets

- Key in server memory only (`TYPESAFE_API_KEY`), read once, used as `Bearer`,
  deleted on session close. Never on disk, in logs, in client code, or behind a
  `VITE_` prefix leaking to the browser.
- The browser only `fetch("/api/...")` calls your proxy; it never sees the key.
- Without a key the system starts degraded by default (`503 typesafe_unconfigured`,
  UI `API key missing`, manual 100% usable).

## Visible fallback, never silent

- Every failure (network, timeout, malformed, no key, low confidence, late)
  degrades to a deterministic local policy and is labelled: `FALLBACK`, `DRY RUN`,
  `OFFLINE SIMULATED POLICY — NOT JEV`, `source: "default" | "off" | "error:<Type>"`.
- Simulated and live carry exclusive labels and costs. A mock never passes as
  Jev; a model `DONE` is never proof (independent verification on the page/reality).
- Every source is always distinguished; a failure over a static scene must
  re-ask until a real answer arrives, not freeze the judgement.
