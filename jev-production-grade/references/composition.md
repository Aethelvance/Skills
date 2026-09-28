# Composition

How to combine questions without paying extra round-trips. One well-built
request beats three sequential ones.

## Speculative fan-out (default)

- **Independent questions over the same `state` go together** in a single POST.
  They run in parallel and cannot see each other: state each speculative premise
  explicitly and let code consume the applicable answers.
- Real examples: `move(choice) + evaluation(score) + tactical(noul)` on one
  position; 8 `score` + `category(choice)` + `is_understandable(noul)` = 10
  decisions in one POST; `kind + form` on the same page.
- A second request only when an earlier answer decides what evidence to fetch,
  what state to build, or what options to offer (e.g. rare family → second step
  with only its members).

## Batches

- One shared `state` + one question per row (`r0..rN`), ~20 rows per request.
  Past ~20-25 accuracy drops measurably: split the batch instead of stretching it.
- The answer must arrive complete or it is an error (`missing answers M of N`).
  Anonymous rows without read-ahead go one by one.
- Measured: 60 questions complete in one POST (0.6s, 2605 in-tok); latency is
  flat vs N and marginal cost is ~30-40 tokens/question. Fan out aggressively.

## Budget

Every question costs. Decide in code what is worth paying for:

- Gatekeeper: clear path + visible goal = zero calls. No changes = reuse the last
  judgement. Only ask when there is something to decide.
- Explicit caps: `call_hz` (e.g. ≤3 Hz), per-episode `call_budget` (e.g. 160),
  `MAX_STEPS` (e.g. 60 actions), `batch_size`, `concurrency` (up to 2× in flight).
- Single-slot queue that drops instead of accumulating; `skipped/late` are counted.
- Unchanged fingerprint → `skipped`: never repay the same judgement.
- `LIMIT` and cheap predicates first: whatever filters without Jev is never
  judged; if the executor asks for it later, batch it with its neighbors.
