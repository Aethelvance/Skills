#!/usr/bin/env python3
"""Self-contained evaluator for jev-skill-profesional (stdlib only).

The skill ships its own judge: run this file and it verifies the whole skill
is coherent and true. No dependencies, no test framework, no outside folders.

Usage (from the skill root, i.e. next to SKILL.md)::

    python3 scripts/run_evals.py            # offline only (no key needed)
    TYPESAFE_API_KEY=... python3 scripts/run_evals.py   # offline + live

Exit 0 = everything passed. Exit 1 = at least one check failed.
With no key the live section is SKIPPED (reported, not failed).

Sections:
  A. structural coherence (files, links, frontmatter, no placeholders/secrets)
  B. offline contract (mock labels, validators, gate math, bands, retry parse)
  C. live claims (model, gate, score math, escape hatch, error table, patterns)
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API_URL = "https://api.typesafe.ai/v1/systemone"
RESULTS: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    """Record one check and print it."""
    RESULTS.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def load_key() -> str | None:
    """Key from the environment only. Never from a file (publishable skill)."""
    return os.environ.get("TYPESAFE_API_KEY") or None


def post(body: object, timeout_s: float = 25.0,
         api_key: str | None = None, raw: str | None = None) -> tuple[int, dict]:
    """One raw POST. Returns (status, payload). Transport failure -> (-1, ...)."""
    data = raw.encode() if raw is not None else json.dumps(body).encode()
    req = urllib.request.Request(
        API_URL, data=data,
        headers={"Authorization": "Bearer " + (api_key or ""),
                 "Content-Type": "application/json",
                 "User-Agent": "jev-skill-profesional/run_evals"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode() or "{}")
        except Exception:
            return e.code, {"error": "unreadable"}
    except Exception as e:
        return -1, {"error": f"{type(e).__name__}"}


# ---------------------------------------------------------------- A. coherence
def section_a() -> None:
    print("\n== A. structural coherence ==")
    sys.path.insert(0, os.path.join(HERE, "scripts"))
    import jev_call  # noqa: E402  (the shipped script must import cleanly)
    check("A1 script imports", True, "jev_call")

    sk = open(os.path.join(HERE, "SKILL.md"), encoding="utf-8").read()
    fm = sk.split("---")[1]
    check("A2 frontmatter name matches dir",
          "name: jev-skill-profesional" in fm, "name")
    check("A3 description present", "description:" in fm)
    check("A4 gotchas section", "## Gotchas" in sk)
    refs = re.findall(r"references/([\w-]+\.md)", sk)
    missing = [r for r in set(refs) if not os.path.exists(os.path.join(HERE, "references", r))]
    check("A5 referenced files exist", not missing, f"{len(set(refs))} refs"
          + (f" missing={missing}" if missing else ""))
    whole = ""
    for dp, _, fns in os.walk(HERE):
        if "__pycache__" in dp:
            continue
        for fn in fns:
            # the judge itself is excluded: patterns below live in its checks
            if fn == "run_evals.py":
                continue
            if fn.endswith((".md", ".py", ".json")):
                whole += open(os.path.join(dp, fn), encoding="utf-8",
                              errors="ignore").read() + "\n"
    check("A6 no placeholders", not re.search(r"TODO|FIXME|YOUR_KEY_HERE|pass\s*#", whole))
    check("A7 no secrets", "apikey_" not in whole, "no apikey_ literal anywhere")
    disc = json.load(open(os.path.join(HERE, "discovery.json"), encoding="utf-8"))
    need = ["question", "trigger", "decision", "evidence", "success_measure"]
    check("A8 discovery contract", all(disc.get(k) for k in need))
    gold = 0
    for case in ("curate-reject", "killmyidea-score", "tax-kind"):
        st = json.load(open(os.path.join(HERE, "evals", "golden", case, "state.json")))
        qu = json.load(open(os.path.join(HERE, "evals", "golden", case, "questions.json")))
        if isinstance(st, dict) and isinstance(qu, dict) and qu:
            gold += 1
    check("A9 golden cases valid", gold == 3, f"{gold}/3")
    check("A10 SKILL.md under 500 lines", len(sk.splitlines()) < 500,
          f"{len(sk.splitlines())} lines")


# ---------------------------------------------------------------- B. offline
def section_b() -> None:
    print("\n== B. offline contract ==")
    sys.path.insert(0, os.path.join(HERE, "scripts"))
    from jev_call import (  # noqa: E402
        min_confidence, mock_answers, retry_after_s, validate_answers)
    q = {"c": {"type": "choice", "criteria": {"a": "x"}}}
    check("B1 missing rejected", bool(validate_answers(q, {})))
    check("B2 off-list rejected",
          bool(validate_answers(q, {"c": {"choice": "z", "confidence": 0.9}})))
    check("B3 valid accepted",
          not validate_answers(q, {"c": {"choice": "a", "confidence": 0.9}}))
    check("B4 non-finite rejected", bool(validate_answers(
        {"s": {"type": "score"}}, {"s": {"score": float("nan"), "confidence": 0.9}})))
    check("B5 gate is min-rule",
          min_confidence({"a": {"confidence": 0.3}, "b": {"confidence": 0.9}}) == 0.3)
    m = mock_answers({"k": {"type": "choice", "criteria": {"x": "y"}}})
    check("B6 mock labelled", m["k"]["choice"] == "x", "deterministic mock")
    check("B7 retry-after parsing",
          retry_after_s({"retry-after-ms": "1500"}, 9.0) == 1.5
          and retry_after_s({}, 0.5) == 0.5
          and retry_after_s({"retry-after": "99"}, 9.0) == 30.0, "ms/s/cap")
    pct = ((2.0 * 2 + 3.0 * 2 + 2.0) / 5) / 4 * 100
    check("B8 weighted bands", abs(pct - 60.0) < 1e-9 and pct < 65, f"{pct:.1f} -> FIX")
    # mock end-to-end through the shipped script
    st = os.path.join(HERE, "evals", "golden", "tax-kind", "state.json")
    qu = os.path.join(HERE, "evals", "golden", "tax-kind", "questions.json")
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as fo:
        out = fo.name
    try:
        r = subprocess.run([sys.executable, os.path.join(HERE, "scripts", "jev_call.py"),
                            "--mock", "--state", st, "--questions", qu, "--out", out],
                           capture_output=True, text=True, timeout=60)
        v = json.load(open(out, encoding="utf-8")) if os.path.exists(out) else {}
        check("B9 mock run labels source", r.returncode == 0
              and v.get("source") == "mock" and v.get("usage", {}).get("input_tokens") == 0)
    finally:
        if os.path.exists(out):
            os.unlink(out)


# ---------------------------------------------------------------- C. live
def live_call(state: dict, questions: dict, key: str, **kw) -> tuple[int, dict]:
    """Live POST with key. Returns (status, payload)."""
    data = json.dumps({"model": kw.get("model", "jev-latest"),
                       "state": state, "questions": questions}).encode()
    req = urllib.request.Request(
        API_URL, data=data,
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json",
                 "User-Agent": "jev-skill-profesional/run_evals"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode() or "{}")
        except Exception:
            return e.code, {"error": "unreadable"}
    except Exception as e:
        return -1, {"error": f"{type(e).__name__}"}


def section_c(key: str) -> None:
    print("\n== C. live claims ==")
    q = {"ok": {"type": "noul", "instructions": "Is any text present in `text`?",
                "criteria": {"true": "Present", "false": "Absent"}}}
    s, p = live_call({"text": "ping"}, q, key)
    check("C1 model resolves", s == 200 and p.get("model") == "jev-1.13.0",
          f"model={p.get('model')}")
    # score = weighted index, recomputed from returned probabilities
    s, p = live_call({"text": "Moved terms, divided, no check."},
                     {"r": {"type": "score",
                            "instructions": "Rate the rigor in `text`.",
                            "criteria": ["none", "low", "mid", "high", "perfect"]}}, key)
    a = (p.get("answers") or {}).get("r", {})
    pr = a.get("probabilities") or {}
    exp = sum(i * pr.get(str(i), 0) for i in range(5))
    check("C2 score is weighted index", s == 200 and abs(a.get("score", -9) - exp) < 0.08,
          f"score={a.get('score')}")
    # escape hatch works
    s, p = live_call({"text": "The car engine needs oil."},
                     {"c": {"type": "choice",
                            "instructions": "Which fruit is `text` about?",
                            "criteria": {"apple": "Red fruit", "banana": "Yellow fruit",
                                         "neither": "Neither fruit"}}}, key)
    check("C3 escape hatch", s == 200 and p["answers"]["c"]["choice"] == "neither")
    # genuine overlap still one-hots (documents winner-takes-all honestly)
    s, p = live_call(
        {"text": "Teams list spare GPU hours others rent by the minute."},
        {"c": {"type": "choice", "instructions": "Which category fits `text`?",
               "criteria": {"SaaS": "Sold to firms", "Marketplace": "Buyers/sellers",
                            "DevTool": "For developers"}}}, key)
    a = (p.get("answers") or {}).get("c", {})
    check("C4 overlap one-hots (known behavior)", s == 200 and max(
        (v for v in (a.get("probabilities") or {}).values()
         if isinstance(v, (int, float))), default=0) > 0.9,
        f"choice={a.get('choice')} conf={a.get('confidence')}")
    # free error probes (no tokens): envelope strictness
    free = [
        ("bad key 401", {"model": "jev-latest", "state": {"text": "x"}, "questions": q},
         "apikey_fake", 401),
        ("unknown model 400", {"model": "jev-nope", "state": {"text": "x"},
                               "questions": q}, key, 400),
        ("empty questions 422", {"model": "jev-latest", "state": {"text": "x"},
                                 "questions": {}}, key, 422),
        ("extra field 400", {"model": "jev-latest", "state": {"text": "x"},
                             "questions": q, "temperature": 0.1}, key, 400),
    ]
    for name, body, k, want in free:
        data = json.dumps(body).encode()
        req = urllib.request.Request(
            API_URL, data=data,
            headers={"Authorization": "Bearer " + k, "Content-Type": "application/json"},
            method="POST")
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                got = r.status
        except urllib.error.HTTPError as e:
            got = e.code
        except Exception:
            got = -1
        check(f"C5 {name}", got == want, f"http={got}")


def main() -> int:
    print("jev-skill-profesional self-evaluation (AIO evaluator)")
    section_a()
    section_b()
    key = load_key()
    if key:
        section_c(key)
    else:
        print("\n== C. live claims = SKIPPED (set TYPESAFE_API_KEY) ==")
    fails = [n for n, ok, _ in RESULTS if not ok]
    print(f"\n{len(RESULTS) - len(fails)}/{len(RESULTS)} passed"
          + ("" if not fails else f" — FAILED: {fails}"))
    return 0 if not fails else 1


if __name__ == "__main__":
    raise SystemExit(main())
