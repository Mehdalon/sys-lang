"""Verify a SYS spec against a codebase: are the symbols each slot names real?"""

from __future__ import annotations

import re
from pathlib import Path

from .schema import SLOTS, UNSPECIFIED, SysSpec


def parse_spec_markdown(md: str) -> SysSpec:
    """Parse a SPEC markdown document back into a SysSpec without re-translating."""
    slots: dict[str, str] = {}
    name = "Spec"
    title = re.search(r"^# SPEC (\w+)", md, flags=re.MULTILINE)
    if title:
        name = title.group(1)
    for slot in SLOTS:
        slots[slot] = UNSPECIFIED
        m = re.search(rf"^## {slot}\s*\n(.*?)(?=^## |\Z)", md, flags=re.MULTILINE | re.DOTALL)
        if m:
            val = m.group(1).strip()
            slots[slot] = val if val and val != "UNSPECIFIED" else UNSPECIFIED
    rewritten_m = re.search(r"^## rewritten_intent\s*\n(.*?)(?=^## |\Z)", md, flags=re.MULTILINE | re.DOTALL)
    return SysSpec(name=name, slots=slots, source_human="", rewritten=(rewritten_m.group(1).strip() if rewritten_m else ""))

_IDENT_RE = re.compile(
    r"\b(?:"  # PascalCase, camelCase, snake_case, or dotted paths
    r"[A-Z][A-Za-z0-9]*"
    r"|[a-z_][A-Za-z0-9_]*"
    r")(?:\.[a-z_][A-Za-z0-9_]*)?\b"
)

STOP = {
    "a", "an", "the", "and", "or", "of", "to", "from", "for", "with", "on", "in", "at",
    "by", "as", "is", "are", "this", "that", "these", "those", "it", "its", "no", "not",
    "none", "min", "max", "via", "vs", "per", "true", "false", "when", "into", "over",
}


def identifiers(text: str) -> set[str]:
    """Extract code-like identifiers: PascalCase, camelCase, snake_case, dotted paths."""
    out = set()
    for m in _IDENT_RE.finditer(text):
        tok = m.group(0)
        if tok.lower() in STOP:
            continue
        if 3 <= len(tok) <= 64:
            out.add(tok)
    return out


def slot_identifiers(spec: SysSpec) -> dict[str, set[str]]:
    seen: set[str] = set()
    result: dict[str, set[str]] = {}
    for slot in SLOTS:
        val = spec.slots.get(slot) or UNSPECIFIED
        if val == UNSPECIFIED or not val.strip():
            continue
        ids = identifiers(val)
        known = set()
        if slot in {"MAP", "OBJ", "C", "FAIL", "EVAL"}:
            known = {"F", "x", "y", "CE", "F1", "PII"}
        result[slot] = {i for i in ids if i not in known}
        seen |= result[slot]
    return result


def scan_code(root: Path) -> tuple[set[str], set[str]]:
    """Return (tokens_found, tokens_missing) symbol vocabularies from source files."""
    if not root.exists():
        raise FileNotFoundError(f"code path not found: {root}")
    vocab: set[str] = set()
    files = 0
    if root.is_file():
        roots = [root]
    else:
        roots = [p for p in root.rglob("*") if p.is_file() and p.suffix in {".py", ".js", ".ts", ".tsx", ".go", ".c", ".h", ".cc", ".rs", ".java", ".mjs"}]
    for p in roots:
        files += 1
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        vocab |= identifiers(text)
        for tok in re.findall(r"\b(?:def|class) ([A-Za-z_][A-Za-z0-9_]*)\b", text):
            vocab.add(tok)
        vocab |= set(re.findall(r"\b[Cc][Aa][Ss][Ee]\b|env|ctx|config|path", text))
    return vocab, {}


def _dotted_matches(ident: str, vocab: set[str]) -> bool:
    if ident in vocab:
        return True
    if "." in ident:
        head, tail = ident.rsplit(".", 1)
        return head in vocab and tail in vocab
    return False


def verify(spec: SysSpec, code_dir: str | Path) -> dict[str, dict[str, bool]]:
    root = Path(code_dir)
    vocab, _ = scan_code(root)
    report: dict[str, dict[str, bool]] = {}
    for slot, ids in slot_identifiers(spec).items():
        if not ids:
            continue
        report[slot] = {ident: _dotted_matches(ident, vocab) for ident in sorted(ids)}
    return report


def verify_report_markdown(report: dict[str, dict[str, bool]]) -> str:
    lines = ["## verify"]
    total_missing = 0
    per_line_found = 0
    for slot, checks in report.items():
        missing = [k for k, v in checks.items() if not v]
        total_missing += len(missing)
        per_line_found += len([k for k, v in checks.items() if v])
        lines.append(f"- {slot}: {len(checks) - len(missing)}/{len(checks)} found")
        for ident in sorted(checks):
            status = "missing" if not checks[ident] else "ok"
            lines.append(f"  - {ident}: {status}")
    lines.append("")
    if total_missing:
        lines.append(f"## status")
        lines.append("")
        lines.append(f"unverified: {total_missing} symbol(s) not found in source")
    else:
        lines.append(f"## status")
        lines.append("")
        lines.append(f"verified ({per_line_found} symbols)")
    return "\n".join(lines)