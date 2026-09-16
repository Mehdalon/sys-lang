#!/usr/bin/env python3
"""Run SYS from the repo root without installing the package."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from syslang.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
