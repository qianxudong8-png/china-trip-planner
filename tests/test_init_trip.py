"""Regression checks for input scope and valid persisted budgets."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "init_trip.py"


class InitTripTests(unittest.TestCase):
    def initialize(self, *extra):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        folder = Path(tmp.name) / "trip"
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(folder), "--destination", "测试目的地",
             "--days", "3", "--people", "2", *extra],
            capture_output=True, text=True,
        )
        return folder, result

    def test_unknown_scope_stays_unknown(self):
        folder, result = self.initialize("--budget-per-person", "5000")
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads((folder / "trip-input.json").read_text())
        self.assertIsNone(data["budget"]["intercity_included"])
        self.assertEqual(data["budget"]["amount"], 5000)
        self.assertEqual(data["people"], 2)

    def test_explicit_scopes_are_preserved(self):
        for scope, expected in (("included", True), ("excluded", False), ("unknown", None)):
            with self.subTest(scope=scope):
                folder, result = self.initialize("--intercity", scope)
                self.assertEqual(result.returncode, 0, result.stderr)
                data = json.loads((folder / "trip-input.json").read_text())
                self.assertIs(data["budget"]["intercity_included"], expected)

    def test_nonfinite_budget_is_rejected_before_writing(self):
        for budget in ("nan", "inf", "-inf"):
            with self.subTest(budget=budget):
                folder, result = self.initialize("--budget-per-person=" + budget)
                self.assertEqual(result.returncode, 2)
                self.assertFalse(folder.exists())

    def test_reinitializing_does_not_replace_known_scope(self):
        folder, result = self.initialize("--intercity", "excluded")
        self.assertEqual(result.returncode, 0, result.stderr)
        original = (folder / "trip-input.json").read_bytes()
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(folder), "--destination", "另一个目的地", "--days", "5"],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 2)
        self.assertEqual((folder / "trip-input.json").read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
