"""MCP server for the Code Review Assistant.

Exposes three tools:
  - get_repository    : fetch GitHub repo metadata
  - get_file_content  : fetch a file from the configured GitHub repo
  - search_docs       : keyword search over local markdown docs

Run directly to start the MCP server over stdio:
    python server.py
"""

import base64
import logging
import os
import time
from collections import deque
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("mcp-code-review")
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_REPO_OWNER = os.getenv("GITHUB_REPO_OWNER", "")
GITHUB_REPO_NAME = os.getenv("GITHUB_REPO_NAME", "")
GITHUB_API_BASE = "https://api.github.com"

DOCS_DIR: Path = Path(__file__).resolve().parent / "docs"

# Simple sliding-window rate limiter
GITHUB_RATE_LIMIT_MAX = 30          # max requests per window
GITHUB_RATE_LIMIT_WINDOW = 60       # window in seconds
_github_request_times: deque = deque()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _github_headers() -> dict:
    """Return headers for GitHub API calls."""
    return {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "mcp-code-review-assistant",
    }


def _check_github_rate_limit() -> Optional[str]:
    """Return None if under the local rate limit, otherwise an error message."""
    now = time.monotonic()
    cutoff = now - GITHUB_RATE_LIMIT_WINDOW
    while _github_request_times and _github_request_times[0] < cutoff:
        _github_request_times.popleft()
    if len(_github_request_times) >= GITHUB_RATE_LIMIT_MAX:
        return (
            f"GitHub rate limit exceeded "
            f"({GITHUB_RATE_LIMIT_MAX} requests / {GITHUB_RATE_LIMIT_WINDOW}s window). "
            f"Please retry shortly."
        )
    return None


def _record_github_request() -> None:
    _github_request_times.append(time.monotonic())


def _validate_repo_config() -> Optional[str]:
    if not GITHUB_REPO_OWNER or not GITHUB_REPO_NAME:
        return "Error: GITHUB_REPO_OWNER and GITHUB_REPO_NAME must be set in the environment."
    if not GITHUB_TOKEN:
        return "Error: GITHUB_TOKEN environment variable is not set."
    return None


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------


def get_repository() -> str:
    """Fetch metadata for the configured GitHub repository."""
    cfg_err = _validate_repo_config()
    if cfg_err:
        return cfg_err
    rate_err = _check_github_rate_limit()
    if rate_err:
        return f"Error: {rate_err}"

    url = f"{GITHUB_API_BASE}/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}"
    try:
        _record_github_request()
        response = requests.get(url, headers=_github_headers(), timeout=10)
    except requests.RequestException as exc:
        return f"Error: failed to call GitHub API: {exc}"

    if response.status_code != 200:
        return (
            f"Error: GitHub API returned status {response.status_code}: "
            f"{response.text[:200]}"
        )

    data = response.json()
    return (
        f"Repository    : {data.get('full_name')}\n"
        f"Description   : {data.get('description') or 'N/A'}\n"
        f"Default branch: {data.get('default_branch')}\n"
        f"Language      : {data.get('language') or 'N/A'}\n"
        f"Stars         : {data.get('stargazers_count', 0)}\n"
        f"Forks         : {data.get('forks_count', 0)}\n"
        f"Open issues   : {data.get('open_issues_count', 0)}\n"
        f"URL           : {data.get('html_url')}"
    )


def get_file_content(path: str) -> str:
    """Fetch a single file's content from the configured GitHub repository."""
    if not path or not path.strip():
        return "Error: file path is required."

    cfg_err = _validate_repo_config()
    if cfg_err:
        return cfg_err
    rate_err = _check_github_rate_limit()
    if rate_err:
        return f"Error: {rate_err}"

    clean_path = path.strip().lstrip("/")
    url = (
        f"{GITHUB_API_BASE}/repos/{GITHUB_REPO_OWNER}/"
        f"{GITHUB_REPO_NAME}/contents/{clean_path}"
    )
    try:
        _record_github_request()
        response = requests.get(url, headers=_github_headers(), timeout=10)
    except requests.RequestException as exc:
        return f"Error: failed to call GitHub API: {exc}"

    if response.status_code == 404:
        return f"Error: file '{clean_path}' not found in repository."
    if response.status_code != 200:
        return (
            f"Error: GitHub API returned status {response.status_code}: "
            f"{response.text[:200]}"
        )

    payload = response.json()
    if isinstance(payload, list):
        names = [item.get("name") for item in payload]
        return f"'{clean_path}' is a directory containing: {', '.join(names)}"

    encoding = payload.get("encoding")
    raw = payload.get("content", "")
    if encoding == "base64":
        try:
            decoded = base64.b64decode(raw).decode("utf-8", errors="replace")
        except Exception as exc:
            return f"Error: could not decode file content: {exc}"
    else:
        decoded = raw
    return f"=== {clean_path} ===\n{decoded}"


def search_docs(query: str) -> str:
    """Search local markdown documentation for the given query."""
    if not query or not query.strip():
        return "Error: search query must not be empty."

    if not DOCS_DIR.exists() or not DOCS_DIR.is_dir():
        return f"Error: Docs directory not found at {DOCS_DIR}."

    needle = query.strip().lower()
    matches = []
    for md_file in sorted(DOCS_DIR.glob("**/*.md")):
        try:
            text = md_file.read_text(encoding="utf-8")
        except OSError:
            continue
        if needle not in text.lower():
            continue
        snippets = []
        for line_no, line in enumerate(text.splitlines(), start=1):
            if needle in line.lower():
                snippets.append(f"  {line_no:>4}: {line.strip()}")
            if len(snippets) >= 5:
                break
        snippet_block = "\n".join(snippets) if snippets else "  (matched in body)"
        matches.append(f"--- {md_file.relative_to(DOCS_DIR)} ---\n{snippet_block}")

    if not matches:
        return f"No matches found for '{query}' in {DOCS_DIR}."
    return "\n\n".join(matches)


# ---------------------------------------------------------------------------
# MCP server registration (optional - only when mcp is installed)
# ---------------------------------------------------------------------------

try:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("code-review-assistant")

    @mcp.tool()
    def get_repository_tool() -> str:
        """Get metadata for the configured GitHub repository."""
        return get_repository()

    @mcp.tool()
    def get_file_content_tool(path: str) -> str:
        """Read the content of a file from the configured GitHub repository."""
        return get_file_content(path)

    @mcp.tool()
    def search_docs_tool(query: str) -> str:
        """Search local markdown docs for a keyword."""
        return search_docs(query)

    def run_server() -> None:
        logger.info("Starting MCP server: code-review-assistant")
        mcp.run()

except ImportError:  # pragma: no cover - mcp is optional for tests
    mcp = None

    def run_server() -> None:
        raise RuntimeError(
            "The 'mcp' package is not installed. Run 'pip install -r requirements.txt'."
        )


if __name__ == "__main__":
    run_server()
