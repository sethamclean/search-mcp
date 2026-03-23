# -*- coding: utf-8 -*-
"""Main entry point for the search_mcp package."""

import os
import sys
import logging
import httpx
from pathlib import Path
from fastmcp import FastMCP
from markitdown import MarkItDown


def _truncate(text: str, max_chars: int) -> str:
    if max_chars <= 0:
        return ""
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1].rstrip() + "…"


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
    def search(
        q: str,
        max_results: int = 5,
        compact: bool = True,
        snippet_chars: int = 160,
    ) -> str:
        """
        Search the SearXNG API for a given query and return the results as markdown.

        Args:
            q (str): The search query string.
            max_results (int): Max number of results to return (default: 5).
            compact (bool): Return compact output with short snippets (default: True).
            snippet_chars (int): Max snippet length in compact mode (default: 160).

        Returns:
            fastapi.Response: Markdown-formatted search results.

        Usage:
            Call this tool with a search query string to retrieve relevant results from the SearXNG API.
            Example: search(q="python programming")
        """
        logger.info(
            "Received search request: q=%s, max_results=%s, compact=%s, snippet_chars=%s",
            q,
            max_results,
            compact,
            snippet_chars,
        )
        max_results = max(1, min(max_results, 20))
        snippet_chars = max(0, min(snippet_chars, 1000))
        params = {"q": q, "format": "json"}

        # Fetch search results using httpx
        with httpx.Client(timeout=10.0) as client:
            try:
                response = client.get(SEARXNG_API_URL, params=params)
                response.raise_for_status()
                data = response.json()
            except httpx.HTTPError as e:
                logger.error(f"HTTP request error: {e}")
                return f"Error fetching search results: {e}"

        results = data.get("results", [])
        if not results:
            return "# Search Results\n\nNo results found."

        # Convert JSON to Markdown
        md_content = "# Search Results\n\n"
        selected = results[:max_results]

        if compact:
            for result in selected:
                title = result.get("title") or "Untitled"
                url = result.get("url") or ""
                snippet = _truncate(
                    str(result.get("content", "")).strip(), snippet_chars
                )
                if url:
                    md_content += f"- [{title}]({url})"
                else:
                    md_content += f"- {title}"
                if snippet:
                    md_content += f" — {snippet}"
                md_content += "\n"
            return md_content

        for result in selected:
            title = result.get("title") or "Untitled"
            url = result.get("url") or ""
            content = str(result.get("content", "")).strip()
            if url:
                md_content += f"## [{title}]({url})\n\n"
            else:
                md_content += f"## {title}\n\n"
            md_content += f"{content}\n\n"
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
