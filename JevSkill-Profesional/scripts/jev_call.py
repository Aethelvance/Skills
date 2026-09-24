#!/usr/bin/env python3
"""Single Jev System One call with typed validation and confidence gating.

One POST of ``state + questions`` to TypeSafe, then fail-closed validation:
a missing answer, a wrong type, or a non-finite number is an error, never a
filled-in verdict. Low confidence gates the verdict instead of acting on it.

Reads the key only from ``TYPESAFE_API_KEY`` (never from argv, to keep it out
of shell history and logs). ``--mock`` returns deterministic fakes labelled
``model: "mock"`` for offline work; mock output is never billable as Jev.

Exit codes: 0 verdict written (possibly gated), 2 transport/validation failure
(no verdict invented), 3 bad CLI usage.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
import time
import urllib.error
import urllib.request

API_DEFAULT = "https://api.typesafe.ai/v1/systemone"
MODEL_DEFAULT = "jev-latest"
RETRYABLE = {408, 429, 529, 500, 502, 503, 504}


def load_json(path: str) -> object:
    """Load a JSON file, raising a clear error on failure."""
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def is_finite_number(value: object) -> bool:
    """Return True for real finite int/float values (rejects NaN/inf/bool)."""
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def mock_answers(questions: dict) -> dict:
    """Build deterministic fake answers labelled as mock, never as Jev."""
    answers: dict = {}
    for name, spec in questions.items():
        qtype = spec.get("type")
        if qtype == "noul":
            answers[name] = {"type": "noul", "noul": 0.1}
        elif qtype == "score":
            answers[name] = {
                "type": "score",
                "score": 2.0,
                "confidence": 0.6,
                "probabilities": {"2": 1.0},
            }
        elif qtype == "choice":
            criteria = spec.get("criteria", {})
            first = next(iter(criteria), "not_in_this_list")
            answers[name] = {
                "type": "choice",
                "choice": first,
                "confidence": 0.6,
                "probabilities": {first: 1.0},
            }
        else:
            raise ValueError(f"question {name!r}: unknown type {qtype!r}")
    return answers


def validate_answers(questions: dict, answers: dict) -> list[str]:
    """Check every question has a well-typed, finite answer. Return error list."""
    errors: list[str] = []
    for name, spec in questions.items():
        qtype = spec.get("type")
        ans = answers.get(name)
        if not isinstance(ans, dict):
            errors.append(f"{name}: answer missing, rejecting")
            continue
        if qtype == "noul":
            if not is_finite_number(ans.get("noul")):
                errors.append(f"{name}: noul not finite, rejecting")
        elif qtype == "score":
            if not is_finite_number(ans.get("score")):
                errors.append(f"{name}: score not finite, rejecting")
            if not is_finite_number(ans.get("confidence", 1.0)):
                errors.append(f"{name}: confidence not finite, rejecting")
        elif qtype == "choice":
            criteria = spec.get("criteria", {})
            choice = ans.get("choice")
            if choice not in criteria:
                errors.append(f"{name}: choice {choice!r} outside criteria, rejecting")
            if not is_finite_number(ans.get("confidence", 1.0)):
                errors.append(f"{name}: confidence not finite, rejecting")
        else:
            errors.append(f"{name}: unknown question type {qtype!r}")
    return errors


def min_confidence(answers: dict) -> float:
    """Return the minimum confidence across answers (absent = 1.0)."""
    confs = [
        ans.get("confidence", 1.0)
        for ans in answers.values()
        if isinstance(ans, dict) and is_finite_number(ans.get("confidence", 1.0))
    ]
    return min(confs) if confs else 1.0


def post_once(endpoint: str, body: dict, api_key: str, timeout_s: float) -> tuple[int, dict, dict]:
    """POST once. Return (status, parsed_json, response_headers)."""
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "JevSkill-Profesional/1.0.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            payload = json.loads(resp.read().decode("utf-8") or "{}")
            return resp.status, payload, dict(resp.headers)
    except urllib.error.HTTPError as exc:
        try:
            payload = json.loads(exc.read().decode("utf-8") or "{}")
        except Exception:
            payload = {"error": f"HTTP {exc.code}"}
        return exc.code, payload, dict(exc.headers or {})


def retry_after_s(headers: dict, default_s: float) -> float:
    """Honor retry-after-ms (or Retry-After), capped at 30s."""
    for key in ("retry-after-ms", "Retry-After-Ms", "retry-after", "Retry-After"):
        if key in headers:
            try:
                raw = float(headers[key])
                if "ms" in key.lower():
                    raw /= 1000.0
                return max(0.0, min(raw, 30.0))
            except (TypeError, ValueError):
                continue
    return default_s


def call_jev(endpoint: str, body: dict, api_key: str, timeout_s: float, max_retries: int) -> tuple[dict, float, str]:
    """POST with backoff on 408/429/529/5xx. Return (payload, latency_s, source)."""
    started = time.monotonic()
    attempt = 0
    while True:
        status, payload, headers = post_once(endpoint, body, api_key, timeout_s)
        if status < 400:
            return payload, time.monotonic() - started, "jev"
        if status not in RETRYABLE or attempt >= max_retries:
            raise RuntimeError(f"TypeSafe HTTP {status}: {json.dumps(payload)[:300]}")
        wait = retry_after_s(headers, default_s=0.5 * (2 ** attempt))
        wait += random.uniform(0, 0.25)
        time.sleep(wait)
        attempt += 1


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse CLI flags."""
    parser = argparse.ArgumentParser(description="One typed Jev System One call.")
    parser.add_argument("--state", required=True, help="Path to state JSON object")
    parser.add_argument("--questions", required=True, help="Path to questions JSON object")
    parser.add_argument("--out", required=True, help="Path to write verdict JSON")
    parser.add_argument("--model", default=MODEL_DEFAULT, help="jev-latest (default) or pinned version")
    parser.add_argument("--endpoint", default=os.environ.get("TYPESAFE_ENDPOINT", API_DEFAULT))
    parser.add_argument("--timeout-ms", type=int, default=12000, help="Per-request timeout in ms")
    parser.add_argument("--max-retries", type=int, default=2, help="Retries on 408/429/529/5xx")
    parser.add_argument("--min-confidence", type=float, default=0.5, help="Gate floor")
    parser.add_argument("--mock", action="store_true", help="Offline deterministic fakes, labelled mock")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    """CLI entry point."""
    try:
        args = parse_args(argv)
    except SystemExit as exc:
        return 3 if exc.code != 0 else 0

    try:
        state = load_json(args.state)
        questions = load_json(args.questions)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"jev_call: cannot load input: {exc}", file=sys.stderr)
        return 3
    if not isinstance(questions, dict) or not questions:
        print("jev_call: questions must be a non-empty object", file=sys.stderr)
        return 3

    t0 = time.monotonic()
    try:
        if args.mock:
            answers = mock_answers(questions)
            usage = {"input_tokens": 0, "output_tokens": 0}
            model, source, latency_s = "mock", "mock", time.monotonic() - t0
        else:
            api_key = os.environ.get("TYPESAFE_API_KEY", "")
            if not api_key:
                print("jev_call: TYPESAFE_API_KEY is not set (or use --mock)", file=sys.stderr)
                return 2
            body = {"model": args.model, "state": state, "questions": questions}
            payload, latency_s, source = call_jev(
                args.endpoint, body, api_key, args.timeout_ms / 1000.0, args.max_retries
            )
            raw_answers = payload.get("answers")
            if not isinstance(raw_answers, dict):
                print("jev_call: 502 response has no answers object, rejecting", file=sys.stderr)
                return 2
            answers = raw_answers
            usage = payload.get("usage", {})
            model = payload.get("model", args.model)
    except (RuntimeError, ValueError, urllib.error.URLError, TimeoutError) as exc:
        print(f"jev_call: Jev call failed: {exc}", file=sys.stderr)
        return 2

    errors = validate_answers(questions, answers)
    if errors:
        for err in errors:
            print(f"jev_call: 502 {err}", file=sys.stderr)
        return 2

    conf_min = min_confidence(answers)
    gated = conf_min >= args.min_confidence
    verdict = {
        "model": model,
        "source": source,
        "answers": answers,
        "confidence_min": conf_min,
        "gated": gated,
        "gate_floor": args.min_confidence,
        "latency_ms": round(latency_s * 1000),
        "usage": usage,
    }
    if not gated:
        verdict["reason"] = f"confidence {conf_min:.2f} below floor {args.min_confidence}"
        print(f"jev_call: gated: {verdict['reason']}", file=sys.stderr)

    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(verdict, fh, indent=2, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
