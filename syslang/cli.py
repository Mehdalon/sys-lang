"""CLI: lint | translate."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .translate import codegen_prompt, lint, translate, translate_file


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="syslang", description="Human → SYS spec translator")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_lint = sub.add_parser("lint", help="list banned mind-verbs")
    p_lint.add_argument("path")

    p_tr = sub.add_parser("translate", help="emit SYS markdown")
    p_tr.add_argument("path")
    p_tr.add_argument("--out", help="write spec here")
    p_tr.add_argument("--prompt", action="store_true", help="also print codegen prompt")

    args = p.parse_args(argv)
    path = Path(args.path)
    text = path.read_text(encoding="utf-8")

    if args.cmd == "lint":
        hits = lint(text)
        if not hits:
            print("clean")
            return 0
        print("banned:", ", ".join(hits))
        return 1

    spec = translate_file(path)
    md = spec.to_markdown()
    if args.out:
        Path(args.out).write_text(md, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(md)
    if getattr(args, "prompt", False):
        print("--- codegen prompt ---")
        print(codegen_prompt(spec))
    missing = spec.missing()
    if missing:
        print(f"# incomplete slots: {', '.join(missing)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
