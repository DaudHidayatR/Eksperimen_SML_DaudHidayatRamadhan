import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "automation", ROOT / "preprocessing/automate_DaudHidayatRamadhan.py"
)
auto = importlib.util.module_from_spec(spec)
spec.loader.exec_module(auto)


class CleaningTests(unittest.TestCase):
    def test_conflicts_remove_all_members_and_keep_literal_text(self):
        rows = [
            ["same", 1, 0, 0, 0],
            ["same", 0, 1, 0, 0],
            ["duplicate", 0, 0, 0, 1],
            ["duplicate", 0, 0, 0, 1],
            ["  Mixed CASE ; punctuation  ", 1, 0, 0, 0],
            [None, 1, 0, 0, 0],
            ["   ", 0, 1, 0, 0],
            ["multi", 1, 1, 0, 0],
            ["zero", 0, 0, 0, 0],
        ]
        clean, report = auto.clean_frame(
            pd.DataFrame(rows, columns=["Sentence"] + auto.LABELS)
        )
        self.assertEqual(
            set(clean.Sentence), {"duplicate", "  Mixed CASE ; punctuation  "}
        )
        self.assertEqual(report["conflicting_rows"], 2)
        self.assertEqual(report["invalid_or_empty_rows"], 4)

    def test_schema_rejected(self):
        with self.assertRaisesRegex(ValueError, "schema"):
            auto.clean_frame(pd.DataFrame({"text": ["hello"]}))

    def test_source_integrity_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, "checksum"):
                auto.preprocess(output=temp, expected_hash="not-the-source")

    def test_executed_notebook_parity_and_repeatability(self):
        expected = json.loads(
            (ROOT / "tests/fixtures/manual-manifest.json").read_text()
        )
        with tempfile.TemporaryDirectory() as temp:
            train, test, actual = auto.preprocess(output=Path(temp) / "first")
            _, _, repeated = auto.preprocess(output=Path(temp) / "second")
            self.assertEqual(expected, actual)
            self.assertEqual(actual, repeated)
            for name in ["train.csv.gz", "test.csv.gz", "manifest.json"]:
                self.assertEqual(
                    (Path(temp) / "first" / name).read_bytes(),
                    (ROOT / "preprocessing/sqli_xss_preprocessing" / name).read_bytes(),
                )
            self.assertTrue(set(train.sample_id).isdisjoint(test.sample_id))
            self.assertEqual(len(train), 19200)
            self.assertEqual(len(test), 4800)


if __name__ == "__main__":
    unittest.main()
