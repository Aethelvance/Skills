# Patterns

Six proven ways to use Jev. Pick by what the app shows, selects, changes, or
delegates; combine freely unless you have a reason not to.

1. **Route + fill.** The request picks a handler and its typed parameters. Ask
   the useful per-branch questions upfront and consume only the relevant branch.
   E.g. `direction(choice)` → price in code; `maneuver + jump_profile` → timing in browser.
2. **Select, don't generate.** Code proposes candidates, Jev picks the index.
   Copy or normalize the source value. E.g. annotated legal moves → `move`;
   DOM nodes `[1..N]` → `operation + <op>_target`; IRS forms → `kind + form`.
3. **Find + judge evidence.** Retrieve candidates, compare relevance against the
   query, keep the useful one. E.g. `rerank`, `hierarchical_classification`;
   rows `r0..rN` against `condition`.
4. **Reusable scoring.** Score dimensions once; weights, thresholds, and views
   change without re-inference. With labels they become classic ML features.
   E.g. 8 dimensions weighted ×2 → `KILL/FIX/SHIP`; `composite-scoring`.
5. **Verify + escalate.** Check claims against evidence; uncertain or failing
   cases go to a person or a reasoning model. E.g. `citation_check`, extraction
   cascades, `tactical(noul)` as a display signal, `understandable<0.3` asking
   for detail.
6. **React to state.** Code retains goal and observations; fresh judgements guide
   the next bounded step. Keep inferred state apart from observed facts and check
   freshness before applying. E.g. drone (commit + risk bleeding speed), Doom
   (4 simultaneous axes per tick), T-Rex (one label per obstacle, timing owned
   by code).

For open brainstorming offer the 2-3 directions that best serve the goal and
recommend a starting point. For a concrete request, pick the pattern and build;
brainstorming is not a mandatory detour.
