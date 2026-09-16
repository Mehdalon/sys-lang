"""SYS document slots."""

from __future__ import annotations

from dataclasses import dataclass, field


SLOTS = ("IN", "OUT", "STATE", "MAP", "OBJ", "C", "FAIL", "EVAL")
UNSPECIFIED = "UNSPECIFIED"


@dataclass
class SysSpec:
    name: str
    slots: dict[str, str] = field(default_factory=dict)
    source_human: str = ""
    rewritten: str = ""

    def missing(self) -> list[str]:
        out = []
        for slot in SLOTS:
            val = (self.slots.get(slot) or "").strip()
            if not val or val == UNSPECIFIED:
                out.append(slot)
        return out

    def to_markdown(self) -> str:
        lines = [
            f"# SPEC {self.name}",
            "",
            "## rewritten_intent",
            "",
            self.rewritten.strip() or UNSPECIFIED,
            "",
        ]
        for slot in SLOTS:
            lines.append(f"## {slot}")
            lines.append("")
            lines.append((self.slots.get(slot) or UNSPECIFIED).strip())
            lines.append("")
        missing = self.missing()
        lines.append("## status")
        lines.append("")
        if missing:
            lines.append("incomplete: " + ", ".join(missing))
        else:
            lines.append("complete")
        lines.append("")
        return "\n".join(lines)
