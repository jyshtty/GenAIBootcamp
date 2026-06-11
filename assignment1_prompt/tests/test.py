"""
Unit tests for genaibootcampassign1 (token counting and tokenizers).
Run: python -m unittest tests.test
Requires: pip install tiktoken (transformers optional for some tests).
"""

import sys
import unittest
from pathlib import Path

# Add repo root so we can import task_1
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    import task_1
except ImportError as e:
    task_1 = None
    _import_error = str(e)


@unittest.skipIf(task_1 is None, "task_1 not importable (install tiktoken, transformers)")
class TestTexts(unittest.TestCase):
    """Tests for the assignment texts dictionary."""

    def test_texts_has_expected_languages(self):
        self.assertIn("English", task_1.texts)
        self.assertIn("Spanish", task_1.texts)
        self.assertIn("Arabic", task_1.texts)
        self.assertIn("Hindi", task_1.texts)

    def test_texts_are_non_empty_strings(self):
        for lang, text in task_1.texts.items():
            self.assertIsInstance(text, str, f"{lang} text should be str")
            self.assertTrue(len(text) > 0, f"{lang} text should not be empty")


@unittest.skipIf(task_1 is None, "task_1 not importable")
class TestCountOpenAITokens(unittest.TestCase):
    """Tests for count_openai_tokens using tiktoken."""

    def test_count_openai_tokens_returns_positive_integer(self):
        result = task_1.count_openai_tokens("gpt-3.5-turbo", task_1.texts["English"])
        self.assertIsInstance(result, int)
        self.assertGreaterEqual(result, 0)

    def test_count_openai_tokens_longer_text_has_more_tokens(self):
        short = "Hi"
        long = task_1.texts["English"]
        short_count = task_1.count_openai_tokens("gpt-4", short)
        long_count = task_1.count_openai_tokens("gpt-4", long)
        self.assertLess(short_count, long_count)

    def test_count_openai_tokens_empty_string(self):
        result = task_1.count_openai_tokens("gpt-4o", "")
        self.assertEqual(result, 0)


@unittest.skipIf(task_1 is None, "task_1 not importable")
class TestLoadHfTokenizer(unittest.TestCase):
    """Tests for load_hf_tokenizer (may return None if model not available)."""

    def test_load_hf_tokenizer_returns_none_or_tokenizer(self):
        result = task_1.load_hf_tokenizer("meta-llama/Meta-Llama-3.1-8B")
        self.assertTrue(result is None or hasattr(result, "encode"))

    def test_load_hf_tokenizer_invalid_returns_none(self):
        result = task_1.load_hf_tokenizer("nonexistent/model-name-xyz")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
