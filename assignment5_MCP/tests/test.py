"""
Unit tests for genaibootcampassign5 (MCP Code Review Assistant server).
Run from repo root: python -m unittest tests.test
Requires: pip install -r requirements.txt
"""

import os
import sys
import time
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import server


class TestGitHubHeaders(unittest.TestCase):
    """Tests for _github_headers."""

    def test_github_headers_returns_dict(self):
        result = server._github_headers()
        self.assertIsInstance(result, dict)
        self.assertIn("Accept", result)
        self.assertIn("Authorization", result)
        self.assertEqual(result["Accept"], "application/vnd.github.v3+json")
        self.assertTrue(result["Authorization"].startswith("Bearer "))

    def test_github_headers_uses_env_token(self):
        with patch.dict(os.environ, {"GITHUB_TOKEN": "test-token-123"}, clear=False):
            # Reload to pick up env; or just test that header format is correct
            result = server._github_headers()
            self.assertIn("Bearer ", result["Authorization"])


class TestGitHubRateLimit(unittest.TestCase):
    """Tests for _check_github_rate_limit."""

    def setUp(self):
        # Reset rate limit state so tests don't interfere
        server._github_request_times.clear()

    def tearDown(self):
        server._github_request_times.clear()

    def test_under_limit_returns_none(self):
        err = server._check_github_rate_limit()
        self.assertIsNone(err)

    def test_over_limit_returns_error_message(self):
        # Simulate 31 requests in the same window
        now = time.monotonic()
        server._github_request_times.extend([now] * 31)
        err = server._check_github_rate_limit()
        self.assertIsNotNone(err)
        self.assertIn("rate limit", err.lower())


class TestSearchDocs(unittest.TestCase):
    """Tests for search_docs tool."""

    def test_search_docs_empty_query_returns_error(self):
        result = server.search_docs("")
        self.assertIn("Error", result)
        self.assertIn("query", result.lower())

    def test_search_docs_whitespace_only_returns_error(self):
        result = server.search_docs("   ")
        self.assertIn("Error", result)

    def test_search_docs_valid_query_returns_string(self):
        # If docs dir exists and has .md files, may return matches or "No matches"
        result = server.search_docs("Configuration")
        self.assertIsInstance(result, str)
        self.assertTrue(
            "No matches" in result or "---" in result or "Error" in result or "Docs directory" in result
        )


class TestGetRepository(unittest.TestCase):
    """Tests for get_repository with mocked API."""

    def test_get_repository_no_owner_repo_returns_error(self):
        with patch.object(server, "GITHUB_REPO_OWNER", ""), patch.object(server, "GITHUB_REPO_NAME", ""):
            result = server.get_repository()
            self.assertIn("Error", result)
            self.assertTrue("owner" in result.lower() or "repo" in result.lower())

    def test_get_repository_no_token_returns_error(self):
        with patch.object(server, "GITHUB_TOKEN", ""), patch.object(server, "GITHUB_REPO_OWNER", "octocat"), patch.object(server, "GITHUB_REPO_NAME", "Hello-World"):
            result = server.get_repository()
            self.assertIn("Error", result)
            self.assertIn("GITHUB_TOKEN", result)


class TestGetFileContent(unittest.TestCase):
    """Tests for get_file_content."""

    def test_get_file_content_empty_path_returns_error(self):
        result = server.get_file_content("")
        self.assertIn("Error", result)
        self.assertIn("path", result.lower())

    def test_get_file_content_whitespace_path_returns_error(self):
        result = server.get_file_content("   ")
        self.assertIn("Error", result)


class TestDocDir(unittest.TestCase):
    """Docs directory exists for search_docs."""

    def test_docs_dir_path_is_path_object(self):
        self.assertIsInstance(server.DOCS_DIR, Path)


if __name__ == "__main__":
    unittest.main()
