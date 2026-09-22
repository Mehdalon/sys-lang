# SYS — Systems Spec Language

Human intent → anthropomorphism-free systems spec → codegen prompt.

## Why

Pedro Domingos asked, on 16 September 2026:

> "We need a non-anthropomorphic vocabulary to talk about AI. Any ideas?"
> — [@pmddomingos](https://x.com/pmddomingos/status/2100032135688339599)

This is one idea, made runnable. `syslang/lexicon.py` holds 29 rewrite rules
that trade mind-verbs for systems verbs — *understands* becomes *encodes / maps*,
*wants* becomes *is scored toward*, *thinks* becomes *assigns score* — and 16 of
those verbs are flagged by `lint` wherever they survive. The eight slots below
are the rest of it: a fixed shape for saying what a system takes, holds, and
emits, without a word that implies it minds the outcome.

## Mac / Homebrew Python 3.14

You must be **inside this repo**, and the folder `syslang/` must sit next to `run.py`.

```bash
cd /path/to/sys-lang
ls
# expect: run.py  syslang/  examples/  tests/  pyproject.toml
```

If you copied files into another project (`fly64`) without the `syslang` package directory, `python3 -m syslang` will fail with `No module named syslang`.

### Option A — no install (recommended starter)

```bash
cd /path/to/sys-lang
python3 run.py lint examples/ticket_triage.human.txt
python3 run.py translate examples/ticket_triage.human.txt
python3 run.py translate examples/ticket_triage.human.txt --prompt
python3 run.py translate examples/ticket_triage.human.txt --out /tmp/ticket.sys.md
```

### Verify — check a spec's symbols against real source

`lint` and `translate` are one-way. `verify` closes the loop: parse an existing
spec, extract the code identifiers each slot names, scan a source tree, and
report `ok`/`missing` per symbol — exposing invented claims before codegen.

```bash
cd /path/to/sys-lang
python3 run.py verify /tmp/ticket.sys.md /path/to/code_base
# - IN: filename: ok  ·  inventory_db: missing
```

`verify` reads a spec file as-is (it does not re-translate or re-guess slots),
supports dotted names (`store.save`), and exits non-zero when any symbol is
missing.

### Option B — install editable

```bash
cd /path/to/sys-lang
python3 -m pip install -e .
python3 -m syslang lint examples/ticket_triage.human.txt
python3 -m syslang translate examples/ticket_triage.human.txt --prompt
```

### Tests

```bash
cd /path/to/sys-lang
python3 -m unittest discover -s tests -p 'test_*.py'
```

Wrong (this is what failed):

```bash
python3 -m unittest tests.test_translate   # needs PYTHONPATH=.
python3 -m syslang                         # needs install or PYTHONPATH=.
```

Equivalent with explicit path:

```bash
cd /path/to/sys-lang
PYTHONPATH=. python3 -m syslang translate examples/ticket_triage.human.txt --prompt
PYTHONPATH=. python3 -m unittest tests.test_translate
```

## Spec slots

`IN` `OUT` `STATE` `MAP` `OBJ` `C` `FAIL` `EVAL`

Banned verbs are rewritten. Empty slots stay `UNSPECIFIED`.
