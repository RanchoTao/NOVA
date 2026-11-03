import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from nova.cli import main


class TestCLI(unittest.TestCase):
    def test_roll_challenge_handoff_smoke(self):
        with tempfile.TemporaryDirectory() as root:
            ideas = str(Path(root) / "ideas.json")
            report = str(Path(root) / "review.json")
            target = str(Path(root) / "handoff.json")
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(main(["roll", "--count", "1", "--seed", "42", "--out", ideas]), 0)
                self.assertEqual(main(["challenge", ideas, "--out", report]), 0)
                self.assertEqual(main(["handoff", ideas, "--out", target]), 0)
            self.assertEqual(json.loads(Path(ideas).read_text())["format"], "nova.idea_batch")
            self.assertEqual(json.loads(Path(report).read_text())["scientific_verdict"], "UNKNOWN")
            self.assertFalse(json.loads(Path(target).read_text())["execution_authorized"])
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(main(["roll", "--count", "1", "--out", ideas]), 2)

    def test_catalog_stdout(self):
        capture = io.StringIO()
        with contextlib.redirect_stdout(capture):
            self.assertEqual(main(["catalog"]), 0)
        self.assertIn("necessity_breaker", capture.getvalue())


if __name__ == "__main__":
    unittest.main()
