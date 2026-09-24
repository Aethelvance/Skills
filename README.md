# Skills

Collection of reusable agent skills (OpenCode, Claude Code, Cursor, etc.).
Each skill is self-contained in its own folder with its `SKILL.md`, `scripts/` and `references/`.

## Available skills

| Skill | Description | Folder |
|-------|-------------|--------|
| jev-skill-profesional | Typed judgement with Jev System One (TypeSafe): `noul / score / choice` verdicts over a structured `state` in a single round-trip. For routing, ranking, extraction, verification, classification, scoring, or gating. | `jev-skill-profesional/` |

## Structure

```text
Skills/
├── README.md                  # this file
├── .gitignore
├── jev-skill-profesional/      # skill 1
│   ├── SKILL.md               # full contract
│   ├── AGENTS.md              # agent summary
│   ├── README.md              # skill install + verify
│   ├── discovery.json
│   ├── scripts/
│   │   ├── jev_call.py        # 1 POST, validates answers, confidence gate
│   │   └── run_evals.py       # built-in evaluator (19 offline + 8 live)
│   ├── references/            # per-topic docs (transport, primitives, etc.)
│   └── evals/                 # golden cases
└── <NewSkill>/                # future skills follow the same pattern
    ├── SKILL.md
    ├── README.md
    ├── scripts/
    └── references/
```

## Installation

Via `skills.sh` (recommended):

```bash
npx skills add Aethelvance/Skills --skill jev-skill-profesional
```

Or copy the skill folder you need to wherever your agent reads skills, for example:

```bash
cp -r jev-skill-profesional/ ~/.agents/skills/
```

No dependencies beyond Python 3 (stdlib) unless a skill's README says otherwise.

## Verification

Each skill ships its own evaluator. Example:

```bash
python3 jev-skill-profesional/scripts/run_evals.py
TYPESAFE_API_KEY=... python3 jev-skill-profesional/scripts/run_evals.py  # includes live checks
```

## Adding a new skill

1. Create a `MyNewSkill/` folder at the root.
2. Include at minimum:
   - `SKILL.md` (name, description, contract, usage)
   - `README.md` (install + verify + example)
   - `scripts/` (executable code, stdlib preferred)
3. Optional but recommended: `AGENTS.md`, `references/`, `evals/`.
4. Update the `Available skills` table in this README.

## Roadmap

- [x] jev-skill-profesional
- [ ] Next skills...
