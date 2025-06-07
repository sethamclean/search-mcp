# -*- coding: utf-8 -*-
"""Main entry point for the search_mcp package."""

import os
import sys
import logging
import httpx
from pathlib import Path
from fastmcp import FastMCP
from markitdown import MarkItDown


def get_log_path() -> Path:
    if sys.platform.startswith("linux"):
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    elif sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:
        base = Path.cwd()
    log_dir = base / "search_mcp"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / "search_mcp.log"


def create_mcp_server() -> FastMCP:
    log_path = get_log_path()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
    logger = logging.getLogger("search_mcp")

    SEARXNG_API_URL = os.environ.get("SEARXNG_API_URL")
    if not SEARXNG_API_URL:
        logger.error("SEARXNG_API_URL environment variable not set")
        raise RuntimeError("SEARXNG_API_URL environment variable not set")

    mcp = FastMCP("search-mcp")

    @mcp.tool
    def search(q: str) -> str:
        """
        Search the SearXNG API for a given query and return the results as markdown.

        Args:
            q (str): The search query string.

        Returns:
            fastapi.Response: Markdown-formatted search results.

        Usage:
            Call this tool with a search query string to retrieve relevant results from the SearXNG API.
            Example: search(q="python programming")
        """
        logger.info(f"Received search request: q={q}")
        params = {"q": q, "format": "json"}
        from urllib.parse import urlencode

        url = f"{SEARXNG_API_URL}?{urlencode(params)}"

        # Fetch search results using httpx
        with httpx.Client() as client:
            try:
                response = client.get(url, params=params)
                data = response.json()
            except httpx.RequestError as e:
                logger.error(f"HTTP request error: {e}")
                return f"Error fetching search results: {e}"

        # Convert JSON to Markdown
        md_content = "# Search Results\n\n"

        for result in data.get("results", []):
            md_content += f"## [{result['title']}]({result['url']})\n\n"
            md_content += f"{result.get('content', '')}\n\n"
        return md_content

    @mcp.tool
    def fetch(url: str) -> str:
        """
        Fetch the content at a given URL and convert it to markdown.

        Args:
            url (str): The URL to fetch and convert.

        Returns:
            fastapi.Response: Markdown-formatted content from the URL.

        Usage:
            Call this tool with a URL to retrieve and convert its content to markdown.
            Example: fetch(url="https://jsonplaceholder.typicode.com/todos/1")
        """
        logger.info(f"Received fetch request: url={url}")
        try:
            md = MarkItDown()
            markdown = md.convert_uri(url).markdown
            return markdown
        except Exception as e:
            logger.error(f"markitdown conversion error: {e}")
            return f"Error fetching url: {e}"

    return mcp


def main() -> None:
    mcp = create_mcp_server()
    logger = logging.getLogger("search_mcp")
    logger.info(f"Starting search_mcp server. Log file: {get_log_path()}")
    mcp.run()


if __name__ == "__main__":
    main()
