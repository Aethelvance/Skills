# jev-skill-profesional

Typed judgement with Jev System One (TypeSafe): `noul / score / choice` answers
over a structured `state` in a single round-trip. Jev judges; your code executes.

## Install

Copy this folder anywhere your agent reads skills from (e.g. `~/.agents/skills/`,
Claude Code, Cursor, OpenCode). No dependencies beyond Python 3 (stdlib only).

## Verify (the skill ships its own evaluator)

```bash
python3 scripts/run_evals.py            # offline: coherence + contract, no key
TYPESAFE_API_KEY=... python3 scripts/run_evals.py   # offline + live claims
```

Exit 0 = 27/27 green (19 offline + 8 live). Without a key the live section is
reported as skipped, never failed. Get a key at `console.typesafe.ai/keys`.

## Use

```bash
export TYPESAFE_API_KEY=...
python3 scripts/jev_call.py --state state.json --questions questions.json --out verdict.json
```

Read `SKILL.md` for the full contract, `references/` for one topic at a time.
