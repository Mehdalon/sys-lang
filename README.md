# SYS — Systems Spec Language

Human intent → anthropomorphism-free systems spec → codegen prompt.

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
