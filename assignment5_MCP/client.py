"""Simple test client that exercises the server tools.

Two modes:
  - default (no mcp install): calls the tool functions in `server` directly.
  - --mcp                    : connects to the MCP server over stdio (requires mcp).

Examples:
    python client.py --test-all
    python client.py --test-github
    python client.py --test-docs --query "Configuration"
"""

import argparse
import asyncio
import sys

import server


def _print_section(title: str) -> None:
    bar = "=" * 60
    print(f"\n{bar}\n{title}\n{bar}")


def test_github_repository() -> None:
    _print_section("get_repository")
    print(server.get_repository())


def test_github_file(path: str) -> None:
    _print_section(f"get_file_content('{path}')")
    print(server.get_file_content(path))


def test_docs_search(query: str) -> None:
    _print_section(f"search_docs('{query}')")
    print(server.search_docs(query))


async def _mcp_smoke_test() -> None:
    """Exercise the live MCP server over stdio."""
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    params = StdioServerParameters(command=sys.executable, args=["server.py"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("Discovered tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")

            print("\nCalling search_docs_tool('Configuration'):")
            result = await session.call_tool("search_docs_tool", {"query": "Configuration"})
            for content in result.content:
                if hasattr(content, "text"):
                    print(content.text)


def main() -> None:
    parser = argparse.ArgumentParser(description="Test client for the MCP code-review server")
    parser.add_argument("--test-all", action="store_true", help="Run every tool against current config")
    parser.add_argument("--test-github", action="store_true", help="Run only GitHub tools")
    parser.add_argument("--test-docs", action="store_true", help="Run only docs search")
    parser.add_argument("--query", default="Configuration", help="Query to use for search_docs")
    parser.add_argument("--path", default="README.md", help="Path to use for get_file_content")
    parser.add_argument("--mcp", action="store_true", help="Talk to the MCP server over stdio (requires mcp)")
    args = parser.parse_args()

    if args.mcp:
        asyncio.run(_mcp_smoke_test())
        return

    ran_anything = False
    if args.test_all or args.test_github:
        test_github_repository()
        test_github_file(args.path)
        ran_anything = True
    if args.test_all or args.test_docs:
        test_docs_search(args.query)
        ran_anything = True

    if not ran_anything:
        parser.print_help()


if __name__ == "__main__":
    main()
