# Integration tests for search_mcp server

import pytest
from fastmcp import Client, FastMCP
from src.search_mcp.main import create_mcp_server


@pytest.fixture
def mcp_server() -> FastMCP:
    return create_mcp_server()


@pytest.mark.asyncio
async def test_search_returns_markdown(mcp_server: FastMCP) -> None:
    async with Client(mcp_server) as client:
        result = await client.call_tool("search", {"q": "test"})
        r = result[0].text.lower()
        assert "test" in r
        assert "#" in r or "-" in r


@pytest.mark.asyncio
async def test_fetch_returns_markdown(mcp_server: FastMCP) -> None:
    url = "https://jsonplaceholder.typicode.com/todos/1"
    async with Client(mcp_server) as client:
        result = await client.call_tool("fetch", {"url": url})
        r = result[0].text.lower()
        assert "userid" in r
        assert "title" in r
