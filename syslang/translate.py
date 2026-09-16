"""Rewrite human text and emit a SYS spec skeleton."""

from __future__ import annotations

import re
from pathlib import Path

from .lexicon import BANNED_TOKENS, REPLACEMENTS
from .schema import UNSPECIFIED, SysSpec


def rewrite(text: str) -> str:
    out = text
    for pattern, repl in REPLACEMENTS:
        out = re.sub(pattern, repl, out, flags=re.IGNORECASE)
    return out


def lint(text: str) -> list[str]:
    hits = []
    lower = text.lower()
    for token in BANNED_TOKENS:
        if re.search(rf"\b{re.escape(token)}\b", lower):
            hits.append(token)
    return sorted(set(hits))


def _guess_name(text: str) -> str:
    words = re.findall(r"[A-Za-z][A-Za-z0-9]+", text)
    if not words:
        return "Untitled"
    picked = [w.capitalize() for w in words[:4] if w.lower() not in {"a", "an", "the", "make", "build"}]
    return "".join(picked[:3]) or "Untitled"


def _heuristic_slots(text: str) -> dict[str, str]:
    """Very small starter heuristics. Unsure → UNSPECIFIED."""
    slots = {k: UNSPECIFIED for k in ("IN", "OUT", "STATE", "MAP", "OBJ", "C", "FAIL", "EVAL")}
    t = text.lower()

    if "ticket" in t:
        slots["IN"] = "ticket : Record{text: str, meta: Record}"
        slots["OUT"] = "result : Record{urgency: enum, reply: str, conf: float[0,1]}"
        slots["STATE"] = "none"
        slots["MAP"] = "embed(text) → classify(urgency) → decode(reply); conf from predictive entropy"
        slots["OBJ"] = "minimize CE(urgency) + toxicity(reply) + latency"
        slots["C"] = "low-confidence → route human; no PII in reply"
        slots["FAIL"] = "empty_text → reject; model_timeout → fallback + human"
        slots["EVAL"] = "macro-F1(urgency); PII_leak_rate == 0"
    else:
        slots["STATE"] = "none  # default until specified"
        slots["MAP"] = f"y = F(x)  # derived from: {text.strip()[:180]}"
    return slots


def translate(text: str) -> SysSpec:
    rewritten = rewrite(text)
    spec = SysSpec(
        name=_guess_name(text),
        source_human=text,
        rewritten=rewritten,
        slots=_heuristic_slots(text),
    )
    return spec


def translate_file(path: str | Path) -> SysSpec:
    return translate(Path(path).read_text(encoding="utf-8"))


CODEGEN_WRAP = """You implement the following SYS spec only.
Do not add behavior that is not in the spec.
If a slot is UNSPECIFIED, ask — do not invent it.
Prefer small pure functions, explicit types, and tests from EVAL + FAIL.

"""


def codegen_prompt(spec: SysSpec) -> str:
    return CODEGEN_WRAP + spec.to_markdown()
