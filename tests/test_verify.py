import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from syslang.verify import parse_spec_markdown, verify


SPEC = """# SPEC Demo

## rewritten_intent
none

## IN
translate_file; MissingSymbol

## OUT
rewrite

## MAP
rewrite; nonexistent_func

## status
complete
"""


class VerifyTests(unittest.TestCase):
    def setUp(self):
        self.code_dir = ROOT / "syslang"

    def test_parse_reads_slots_from_markdown(self):
        spec = parse_spec_markdown(SPEC)
        self.assertEqual(spec.slots["IN"], "translate_file; MissingSymbol")
        self.assertEqual(spec.slots["OUT"], "rewrite")
        self.assertEqual(spec.slots["STATE"], "UNSPECIFIED")

    def test_verify_finds_real_and_flags_missing(self):
        spec = parse_spec_markdown(SPEC)
        report = verify(spec, self.code_dir)
        self.assertIn("IN", report)
        self.assertEqual(report["IN"]["translate_file"], True)
        self.assertEqual(report["IN"]["MissingSymbol"], False)
        self.assertEqual(report["MAP"]["rewrite"], True)
        self.assertEqual(report["MAP"]["nonexistent_func"], False)

    def test_verify_exits_via_missing_count(self):
        spec = parse_spec_markdown(SPEC)
        report = verify(spec, self.code_dir)
        missing = sum(not ok for checks in report.values() for ok in checks.values())
        self.assertGreater(missing, 0)

    def test_camelcase_js_identifiers_found(self):
        import tempfile

        js = "function renderRack() {} function renderModules() {} function log() {}"
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "ui.js").write_text(js)
            spec = parse_spec_markdown("# SPEC X\n## MAP\nrenderRack; renderModules\n## status\ncomplete\n")
            report = verify(spec, d)
        self.assertEqual(report["MAP"]["renderRack"], True)
        self.assertEqual(report["MAP"]["renderModules"], True)

    def test_dotted_identifiers_resolve(self):
        import tempfile

        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "app.py").write_text("class Store:\n    def save(self): pass\n")
            spec = parse_spec_markdown("# SPEC X\n## FAIL\nStore.save\n## status\ncomplete\n")
            report = verify(spec, d)
        self.assertEqual(report["FAIL"]["Store.save"], True)


if __name__ == "__main__":
    unittest.main()