# Integration tests for search_mcp server

import os
from unittest.mock import Mock, patch

import pytest
from fastmcp import Client, FastMCP

from src.search_mcp.main import _truncate, create_mcp_server


@pytest.fixture
def mcp_server() -> FastMCP:
    os.environ.setdefault("SEARXNG_API_URL", "http://127.0.0.1:8080/search")
    return create_mcp_server()


def test_truncate_shorter_than_limit() -> None:
    assert _truncate("hello", 10) == "hello"


def test_truncate_longer_than_limit() -> None:
    assert _truncate("abcdefghij", 5) == "abcd…"


def test_truncate_zero_chars() -> None:
    assert _truncate("hello", 0) == ""


def _result_text(result: object) -> str:
    # fastmcp Client.call_tool returns a CallToolResult in recent versions.
    # Prefer `data` (string tool return), then fallback to first text content.
    data = getattr(result, "data", None)
    if isinstance(data, str):
        return data
    content = getattr(result, "content", None)
    if isinstance(content, list) and content:
        text = getattr(content[0], "text", None)
        if isinstance(text, str):
            return text
    raise AssertionError("Unable to extract text from call_tool result")


@pytest.mark.asyncio
async def test_search_returns_markdown(mcp_server: FastMCP) -> None:
    mock_payload = {
        "results": [
            {
                "title": "Result One",
                "url": "https://example.com/1",
                "content": "A" * 300,
            },
            {
                "title": "Result Two",
                "url": "https://example.com/2",
                "content": "second snippet",
            },
        ]
    }
    mock_response = Mock()
    mock_response.json.return_value = mock_payload
    mock_response.raise_for_status.return_value = None

    async with Client(mcp_server) as client:
        with patch("src.search_mcp.main.httpx.Client") as mock_client_cls:
            mock_client = mock_client_cls.return_value.__enter__.return_value
            mock_client.get.return_value = mock_response
            result = await client.call_tool("search", {"q": "test"})

        r = _result_text(result).lower()
        assert "# search results" in r
        assert "- [result one](https://example.com/1)" in r
        assert "- [result two](https://example.com/2)" in r
        assert "aaaaaaaaaa" in r
        # compact mode should not emit full-detail headings
        assert "## [result one]" not in r


@pytest.mark.asyncio
async def test_search_can_disable_compact_mode(mcp_server: FastMCP) -> None:
    mock_payload = {
        "results": [
            {
                "title": "Detailed Result",
                "url": "https://example.com/detailed",
                "content": "full content block",
            }
        ]
    }
    mock_response = Mock()
    mock_response.json.return_value = mock_payload
    mock_response.raise_for_status.return_value = None

    async with Client(mcp_server) as client:
        with patch("src.search_mcp.main.httpx.Client") as mock_client_cls:
            mock_client = mock_client_cls.return_value.__enter__.return_value
            mock_client.get.return_value = mock_response
            result = await client.call_tool(
                "search",
                {"q": "test", "compact": False, "max_results": 1},
            )

        r = _result_text(result)
        assert "## [Detailed Result](https://example.com/detailed)" in r
        assert "full content block" in r


@pytest.mark.asyncio
async def test_fetch_returns_markdown(mcp_server: FastMCP) -> None:
    url = "https://jsonplaceholder.typicode.com/todos/1"
    async with Client(mcp_server) as client:
        result = await client.call_tool("fetch", {"url": url})
        r = _result_text(result).lower()
        assert "userid" in r
        assert "title" in r
