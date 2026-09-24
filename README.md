# Skills

Colección de skills reutilizables para agentes (OpenCode, Claude Code, Cursor, etc.).
Cada skill es autocontenida en su propia carpeta con su `SKILL.md`, `scripts/` y `references/`.

## Skills disponibles

| Skill | Descripción | Carpeta |
|-------|-------------|---------|
| JevSkill-Profesional | Juicio tipado con Jev System One (TypeSafe): veredictos `noul / score / choice` sobre un `state` estructurado en un solo round-trip. Para routing, ranking, extracción, verificación, clasificación, scoring o gating. | `JevSkill-Profesional/` |

## Estructura

```text
Skills/
├── README.md                  # este archivo
├── .gitignore
├── JevSkill-Profesional/      # skill 1
│   ├── SKILL.md               # contrato completo
│   ├── AGENTS.md              # resumen para agentes
│   ├── README.md              # install + verify de la skill
│   ├── discovery.json
│   ├── scripts/
│   │   ├── jev_call.py        # 1 POST, valida respuestas, gate de confianza
│   │   └── run_evals.py       # evaluador built-in (19 offline + 8 live)
│   ├── references/            # docs por tema (transport, primitives, etc.)
│   └── evals/                 # casos golden
└── <NuevaSkill>/              # futuras skills siguen el mismo patrón
    ├── SKILL.md
    ├── README.md
    ├── scripts/
    └── references/
```

## Instalación

Copia la carpeta de la skill que necesites a donde tu agente lea skills, por ejemplo:

```bash
cp -r JevSkill-Profesional/ ~/.agents/skills/
```

No hay dependencias más allá de Python 3 (stdlib) salvo que el README de cada skill indique lo contrario.

## Verificación

Cada skill trae su propio evaluador. Ejemplo:

```bash
python3 JevSkill-Profesional/scripts/run_evals.py
TYPESAFE_API_KEY=... python3 JevSkill-Profesional/scripts/run_evals.py  # incluye checks live
```

## Añadir una nueva skill

1. Crea una carpeta `MiNuevaSkill/` en la raíz.
2. Incluye como mínimo:
   - `SKILL.md` (nombre, descripción, contrato, uso)
   - `README.md` (install + verify + ejemplo)
   - `scripts/` (código ejecutable, stdlib preferente)
3. Opcional pero recomendado: `AGENTS.md`, `references/`, `evals/`.
4. Actualiza la tabla de `Skills disponibles` de este README.

## Roadmap

- [x] JevSkill-Profesional
- [ ] Próximas skills...
