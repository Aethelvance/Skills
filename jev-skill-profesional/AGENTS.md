# jev-skill-profesional

Use this skill for typed judgement with Jev System One (TypeSafe): `noul / score /
choice` answers over a structured `state` in a single round-trip.

Run:

```bash
export TYPESAFE_API_KEY=...
python3 scripts/jev_call.py --state state.json --questions questions.json --out verdict.json
```

Jev judges; code executes. Gate on `confidence < 0.5`, fail closed with `502` on
malformed answers, and always label the source (`jev` / `mock` / `error:<Type>`).
Full contract in `SKILL.md`; read `references/` for one topic at a time.

## Gotchas

- `jev-latest` currently resolves to `jev-1.13.0`.
- `noul ≈ 0.5` is uncertainty between yes/no, not medium intensity.
- Late or stale judgements are discarded, never applied retroactively.
- `choice` confidence ≈1.0 does not mean a clear case; `< 0.5` means bad fit.
- `score` is an index into your criteria levels; normalize before comparing.
