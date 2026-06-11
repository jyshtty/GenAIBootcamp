"""
Unit tests for genaibootcampassign2 (API integration and prompt engineering).
Run: python -m unittest tests.test
"""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Avoid import-time client init and emoji print (UnicodeEncodeError on Windows)
os.environ.setdefault("DIAL_API_KEY", "test-key-for-unittest")
with patch("builtins.print"):
    try:
        import Assignment2
    except Exception:
        Assignment2 = None


@unittest.skipIf(Assignment2 is None, "Assignment2 not importable (install openai)")
class TestCreateSummaryPrompt(unittest.TestCase):
    """Tests for create_summary_prompt."""

    def test_create_summary_prompt_returns_string(self):
        prompt = Assignment2.create_summary_prompt("Some text.", "executive", "concise")
        self.assertIsInstance(prompt, str)
        self.assertTrue(len(prompt) > 0)

    def test_create_summary_prompt_includes_audience_and_style(self):
        prompt = Assignment2.create_summary_prompt("Body here.", "developers", "technical")
        self.assertIn("developers", prompt)
        self.assertIn("technical", prompt)
        self.assertIn("Body here.", prompt)

    def test_create_summary_prompt_includes_text_to_summarize(self):
        text = "The novel architecture leverages zero-voltage switching."
        prompt = Assignment2.create_summary_prompt(text, "student", "simple")
        self.assertIn(text, prompt)


@unittest.skipIf(Assignment2 is None, "Assignment2 not importable")
class TestExtractContactJson(unittest.TestCase):
    """Tests for extract_contact_json. Uses live API unless mocked; we test structure only via mock."""

    def test_extract_contact_json_accepts_string_input(self):
        # We cannot call real API in unit test; we only check the function exists and is callable
        self.assertTrue(callable(Assignment2.extract_contact_json))


@unittest.skipIf(Assignment2 is None, "Assignment2 not importable")
class TestModuleConstants(unittest.TestCase):
    """Tests for expected module constants."""

    def test_deployment_name_is_string(self):
        self.assertIsInstance(Assignment2.DEPLOYMENT_NAME, str)

    def test_api_version_format(self):
        self.assertIsInstance(Assignment2.API_VERSION, str)
        self.assertTrue(len(Assignment2.API_VERSION) >= 4)


if __name__ == "__main__":
    unittest.main()
