import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from syslang.translate import lint, rewrite, translate


class TranslateTests(unittest.TestCase):
    def test_rewrite_strips_mind_verbs(self):
        raw = "The model understands tickets and decides urgency."
        out = rewrite(raw).lower()
        self.assertNotIn("understands", out)
        self.assertNotIn("decides", out)
        self.assertTrue("encodes" in out or "maps" in out)

    def test_lint_finds_banned(self):
        hits = lint("It knows and wants to help.")
        self.assertIn("knows", hits)
        self.assertTrue("wants" in hits or "want" in hits)

    def test_ticket_slots_filled(self):
        text = (ROOT / "examples" / "ticket_triage.human.txt").read_text()
        spec = translate(text)
        self.assertNotEqual(spec.slots["IN"], "UNSPECIFIED")
        self.assertNotEqual(spec.slots["FAIL"], "UNSPECIFIED")
        self.assertIn("SPEC", spec.to_markdown())


if __name__ == "__main__":
    unittest.main()
