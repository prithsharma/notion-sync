#!/usr/bin/env python3
"""
Notion REST API Client for notion-sync

This module handles all communication with Notion's REST API v1.
Provides methods for fetching, creating, and updating pages and blocks.

Usage:
    from notion_api import NotionAPIClient

    client = NotionAPIClient(api_key="secret_xxx")
    page = client.fetch_page("page_id_here")
    print(page['title'], page['content'])
"""

import json
import re
import time
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse, parse_qs
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


class NotionAPIError(Exception):
    """Base exception for Notion API errors"""
    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class NotionRateLimitError(NotionAPIError):
    """Raised when rate limit is hit"""
    def __init__(self, retry_after: int = 60):
        super().__init__(f"Rate limit exceeded. Retry after {retry_after} seconds.", 429)
        self.retry_after = retry_after


class NotionAPIClient:
    """
    Notion REST API v1 client

    Handles all communication with Notion's API including:
    - Fetching pages and blocks
    - Creating and updating pages
    - Converting between Notion blocks and markdown
    - Search functionality
    """

    API_BASE = "https://api.notion.com/v1"
    API_VERSION = "2022-06-28"

    def __init__(self, api_key: str, rate_limit_retry: bool = True):
        """
        Initialize Notion API client

        Args:
            api_key: Notion integration token (starts with 'secret_')
            rate_limit_retry: Whether to automatically retry on rate limit (default: True)
        """
        if not api_key:
            raise ValueError("API key is required")

        self.api_key = api_key
        self.rate_limit_retry = rate_limit_retry
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Notion-Version": self.API_VERSION,
            "Content-Type": "application/json"
        }

    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None,
                 retry_count: int = 3) -> Dict:
        """
        Make HTTP request to Notion API

        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            endpoint: API endpoint (e.g., '/pages/abc123')
            data: Request payload for POST/PATCH
            retry_count: Number of retries on rate limit

        Returns:
            Response data as dict

        Raises:
            NotionAPIError: On API errors
            NotionRateLimitError: On rate limit (if retry disabled)
        """
        url = f"{self.API_BASE}{endpoint}"

        # Prepare request
        headers = self._headers.copy()
        req_data = None
        if data is not None:
            req_data = json.dumps(data).encode('utf-8')

        request = Request(url, data=req_data, headers=headers, method=method)

        for attempt in range(retry_count):
            try:
                with urlopen(request, timeout=30) as response:
                    body = response.read().decode('utf-8')
                    # Handle empty responses (e.g., from DELETE)
                    if not body:
                        return {}
                    return json.loads(body)

            except HTTPError as e:
                error_body = e.read().decode('utf-8')
                try:
                    error_data = json.loads(error_body)
                    error_message = error_data.get('message', str(e))
                except json.JSONDecodeError:
                    error_message = error_body or str(e)

                # Handle rate limiting (429)
                if e.code == 429:
                    retry_after = int(e.headers.get('Retry-After', 60))
                    if self.rate_limit_retry and attempt < retry_count - 1:
                        print(f"Rate limited. Waiting {retry_after}s before retry...")
                        time.sleep(retry_after)
                        continue
                    else:
                        raise NotionRateLimitError(retry_after)

                # Other HTTP errors
                raise NotionAPIError(
                    f"API request failed: {error_message}",
                    status_code=e.code,
                    response=error_data if 'error_data' in locals() else None
                )

            except URLError as e:
                if attempt < retry_count - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                raise NotionAPIError(f"Network error: {str(e)}")

        raise NotionAPIError("Max retries exceeded")

    def _get_page(self, page_id: str) -> Dict:
        """
        Get page metadata

        Args:
            page_id: Notion page ID

        Returns:
            Page object from API
        """
        page_id = self._clean_id(page_id)
        return self._request("GET", f"/pages/{page_id}")

    def _get_blocks(self, block_id: str, accumulator: Optional[List] = None) -> List[Dict]:
        """
        Get all child blocks recursively with pagination

        Args:
            block_id: Parent block/page ID
            accumulator: For internal recursion

        Returns:
            List of all blocks (nested)
        """
        if accumulator is None:
            accumulator = []

        block_id = self._clean_id(block_id)
        cursor = None

        while True:
            # Build query params
            params = {"page_size": 100}
            if cursor:
                params["start_cursor"] = cursor

            # Make request
            query_string = "&".join(f"{k}={v}" for k, v in params.items())
            endpoint = f"/blocks/{block_id}/children?{query_string}"
            response = self._request("GET", endpoint)

            blocks = response.get("results", [])

            # Process each block
            for block in blocks:
                accumulator.append(block)

                # Recursively get children if block has them
                if block.get("has_children", False):
                    block["children"] = []
                    self._get_blocks(block["id"], block["children"])

            # Check for more pages
            cursor = response.get("next_cursor")
            if not cursor:
                break

        return accumulator

    def _delete_block(self, block_id: str) -> None:
        """
        Delete a block (moves to trash)

        Args:
            block_id: Block ID to delete
        """
        block_id = self._clean_id(block_id)
        self._request("DELETE", f"/blocks/{block_id}")

    def _append_blocks(self, block_id: str, blocks: List[Dict]) -> Dict:
        """
        Append blocks as children of a block/page

        Args:
            block_id: Parent block/page ID
            blocks: List of block objects to append

        Returns:
            API response
        """
        block_id = self._clean_id(block_id)
        return self._request("PATCH", f"/blocks/{block_id}/children", {
            "children": blocks
        })

    def _extract_title(self, page: Dict) -> str:
        """
        Extract title from page properties

        Args:
            page: Page object from API

        Returns:
            Page title as string
        """
        properties = page.get("properties", {})

        # Try 'title' property first (most common)
        if "title" in properties:
            title_prop = properties["title"]
            if title_prop.get("type") == "title":
                title_array = title_prop.get("title", [])
                if title_array:
                    return "".join(item.get("plain_text", "") for item in title_array)

        # Try 'Name' property (common in databases)
        if "Name" in properties:
            name_prop = properties["Name"]
            if name_prop.get("type") == "title":
                title_array = name_prop.get("title", [])
                if title_array:
                    return "".join(item.get("plain_text", "") for item in title_array)

        # Search for any title-type property
        for prop_name, prop_value in properties.items():
            if prop_value.get("type") == "title":
                title_array = prop_value.get("title", [])
                if title_array:
                    return "".join(item.get("plain_text", "") for item in title_array)

        return "Untitled"

    def _get_parent_title(self, page: Dict) -> Optional[str]:
        """
        Get parent page title

        Args:
            page: Page object from API

        Returns:
            Parent page title or None if no parent/workspace root
        """
        parent = page.get("parent", {})
        parent_type = parent.get("type")

        if parent_type == "page_id":
            parent_id = parent.get("page_id")
            try:
                parent_page = self._get_page(parent_id)
                return self._extract_title(parent_page)
            except NotionAPIError:
                return None
        elif parent_type == "database_id":
            # Could fetch database title, but skip for now
            return None

        return None

    def _clean_id(self, page_id: str) -> str:
        """
        Clean and normalize Notion ID or URL

        Args:
            page_id: Page ID or URL

        Returns:
            Clean page ID (32 hex chars with dashes)
        """
        # If it's a URL, extract ID
        if page_id.startswith("http"):
            # Parse URL - ID is usually last part or in query param
            parsed = urlparse(page_id)
            path_parts = parsed.path.strip('/').split('/')
            if path_parts:
                page_id = path_parts[-1]

            # Handle notion.so URLs with ID in path
            if '-' in page_id:
                # Format: "Page-Title-abc123def456"
                page_id = page_id.split('-')[-1]

        # Remove dashes
        page_id = page_id.replace('-', '')

        # Validate format (should be 32 hex chars)
        if not re.match(r'^[a-f0-9]{32}$', page_id.lower()):
            raise ValueError(f"Invalid Notion page ID: {page_id}")

        # Add dashes in standard format: 8-4-4-4-12
        return f"{page_id[:8]}-{page_id[8:12]}-{page_id[12:16]}-{page_id[16:20]}-{page_id[20:]}"

    def _blocks_to_markdown(self, blocks: List[Dict], level: int = 0) -> str:
        """
        Convert Notion blocks to Notion-flavored Markdown

        Args:
            blocks: List of block objects
            level: Indentation level for nested blocks

        Returns:
            Markdown string
        """
        lines = []
        indent = "  " * level

        for block in blocks:
            block_type = block.get("type")
            block_content = block.get(block_type, {})

            # Paragraph
            if block_type == "paragraph":
                text = self._rich_text_to_markdown(block_content.get("rich_text", []))
                if text:
                    lines.append(f"{indent}{text}")
                    lines.append("")

            # Headings
            elif block_type in ["heading_1", "heading_2", "heading_3"]:
                level_map = {"heading_1": "#", "heading_2": "##", "heading_3": "###"}
                text = self._rich_text_to_markdown(block_content.get("rich_text", []))
                lines.append(f"{indent}{level_map[block_type]} {text}")
                lines.append("")

            # Lists
            elif block_type == "bulleted_list_item":
                text = self._rich_text_to_markdown(block_content.get("rich_text", []))
                lines.append(f"{indent}- {text}")
                # Handle nested children
                if block.get("children"):
                    lines.append(self._blocks_to_markdown(block["children"], level + 1))

            elif block_type == "numbered_list_item":
                text = self._rich_text_to_markdown(block_content.get("rich_text", []))
                lines.append(f"{indent}1. {text}")
                # Handle nested children
                if block.get("children"):
                    lines.append(self._blocks_to_markdown(block["children"], level + 1))

            # Code block
            elif block_type == "code":
                language = block_content.get("language", "")
                text = self._rich_text_to_markdown(block_content.get("rich_text", []))
                lines.append(f"{indent}```{language}")
                lines.append(f"{indent}{text}")
                lines.append(f"{indent}```")
                lines.append("")

            # Quote
            elif block_type == "quote":
                text = self._rich_text_to_markdown(block_content.get("rich_text", []))
                lines.append(f"{indent}> {text}")
                lines.append("")

            # Divider
            elif block_type == "divider":
                lines.append(f"{indent}---")
                lines.append("")

            # Toggle (preserve as details tag)
            elif block_type == "toggle":
                text = self._rich_text_to_markdown(block_content.get("rich_text", []))
                lines.append(f"{indent}<details>")
                lines.append(f"{indent}<summary>{text}</summary>")
                if block.get("children"):
                    lines.append(self._blocks_to_markdown(block["children"], level))
                lines.append(f"{indent}</details>")
                lines.append("")

            # Callout (preserve as XML tag)
            elif block_type == "callout":
                icon = block_content.get("icon", {})
                icon_str = icon.get("emoji", "💡") if icon.get("type") == "emoji" else "💡"
                color = block_content.get("color", "gray")
                text = self._rich_text_to_markdown(block_content.get("rich_text", []))
                lines.append(f'{indent}<callout icon="{icon_str}" color="{color}">')
                lines.append(f"{indent}{text}")
                if block.get("children"):
                    lines.append(self._blocks_to_markdown(block["children"], level))
                lines.append(f"{indent}</callout>")
                lines.append("")

            # To-do
            elif block_type == "to_do":
                checked = block_content.get("checked", False)
                checkbox = "[x]" if checked else "[ ]"
                text = self._rich_text_to_markdown(block_content.get("rich_text", []))
                lines.append(f"{indent}- {checkbox} {text}")

            # Child page (preserve as link)
            elif block_type == "child_page":
                title = block_content.get("title", "Untitled")
                lines.append(f"{indent}[[{title}]]")
                lines.append("")

            # Link to page
            elif block_type == "link_to_page":
                page_id = block_content.get("page_id", "")
                lines.append(f"{indent}[Link to page]({page_id})")
                lines.append("")

            # Table (preserve as XML for now - complex to convert)
            elif block_type == "table":
                width = block_content.get("table_width", 0)
                lines.append(f'{indent}<table width="{width}">')
                if block.get("children"):
                    lines.append(self._blocks_to_markdown(block["children"], level + 1))
                lines.append(f"{indent}</table>")
                lines.append("")

            # Table row
            elif block_type == "table_row":
                cells = block_content.get("cells", [])
                row = " | ".join(self._rich_text_to_markdown(cell) for cell in cells)
                lines.append(f"{indent}| {row} |")

            # Bookmark
            elif block_type == "bookmark":
                url = block_content.get("url", "")
                caption = self._rich_text_to_markdown(block_content.get("caption", []))
                title = caption if caption else url
                lines.append(f"{indent}[{title}]({url})")
                lines.append("")

            # Image, video, file (preserve as markdown)
            elif block_type in ["image", "video", "file"]:
                url = block_content.get("external", {}).get("url") or \
                      block_content.get("file", {}).get("url", "")
                caption = self._rich_text_to_markdown(block_content.get("caption", []))

                if block_type == "image":
                    alt_text = caption if caption else "image"
                    lines.append(f"{indent}![{alt_text}]({url})")
                else:
                    label = caption if caption else block_type
                    lines.append(f"{indent}[{label}]({url})")
                lines.append("")

            # Unsupported block types - preserve as comment
            else:
                lines.append(f"{indent}<!-- Unsupported block type: {block_type} -->")
                lines.append("")

        return "\n".join(lines)

    def _rich_text_to_markdown(self, rich_text: List[Dict]) -> str:
        """
        Convert Notion rich text array to markdown string

        Args:
            rich_text: Array of rich text objects

        Returns:
            Markdown string with formatting
        """
        parts = []

        for text_obj in rich_text:
            content = text_obj.get("plain_text", "")
            annotations = text_obj.get("annotations", {})
            href = text_obj.get("href")

            # Apply formatting
            if annotations.get("bold"):
                content = f"**{content}**"
            if annotations.get("italic"):
                content = f"*{content}*"
            if annotations.get("strikethrough"):
                content = f"~~{content}~~"
            if annotations.get("code"):
                content = f"`{content}`"

            # Apply link
            if href:
                content = f"[{content}]({href})"

            parts.append(content)

        return "".join(parts)

    def _markdown_to_blocks(self, markdown: str) -> List[Dict]:
        """
        Convert markdown to Notion block objects (basic implementation)

        Args:
            markdown: Markdown string

        Returns:
            List of block objects for Notion API

        Note:
            This is a basic implementation. Rich blocks (toggle, callout, etc.)
            should be preserved from the original block data when possible.
        """
        blocks = []
        lines = markdown.split('\n')
        i = 0

        while i < len(lines):
            line = lines[i].rstrip()

            # Skip empty lines (will be paragraph breaks)
            if not line:
                i += 1
                continue

            # Heading 1
            if line.startswith('# '):
                blocks.append({
                    "object": "block",
                    "type": "heading_1",
                    "heading_1": {
                        "rich_text": [{"type": "text", "text": {"content": line[2:]}}]
                    }
                })
                i += 1

            # Heading 2
            elif line.startswith('## '):
                blocks.append({
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": line[3:]}}]
                    }
                })
                i += 1

            # Heading 3
            elif line.startswith('### '):
                blocks.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [{"type": "text", "text": {"content": line[4:]}}]
                    }
                })
                i += 1

            # Code block
            elif line.startswith('```'):
                language = line[3:].strip() or "plain text"
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].startswith('```'):
                    code_lines.append(lines[i])
                    i += 1
                blocks.append({
                    "object": "block",
                    "type": "code",
                    "code": {
                        "rich_text": [{"type": "text", "text": {"content": '\n'.join(code_lines)}}],
                        "language": language
                    }
                })
                i += 1  # Skip closing ```

            # Bulleted list
            elif line.startswith('- ') and not line.startswith('- [ ]') and not line.startswith('- [x]'):
                blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": line[2:]}}]
                    }
                })
                i += 1

            # Numbered list
            elif re.match(r'^\d+\.\s', line):
                content = re.sub(r'^\d+\.\s', '', line)
                blocks.append({
                    "object": "block",
                    "type": "numbered_list_item",
                    "numbered_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": content}}]
                    }
                })
                i += 1

            # To-do
            elif line.startswith('- [ ]') or line.startswith('- [x]'):
                checked = line.startswith('- [x]')
                content = line[6:].strip()
                blocks.append({
                    "object": "block",
                    "type": "to_do",
                    "to_do": {
                        "rich_text": [{"type": "text", "text": {"content": content}}],
                        "checked": checked
                    }
                })
                i += 1

            # Quote
            elif line.startswith('> '):
                blocks.append({
                    "object": "block",
                    "type": "quote",
                    "quote": {
                        "rich_text": [{"type": "text", "text": {"content": line[2:]}}]
                    }
                })
                i += 1

            # Divider
            elif line == '---':
                blocks.append({
                    "object": "block",
                    "type": "divider",
                    "divider": {}
                })
                i += 1

            # Preserve rich blocks as-is (details, callout, etc.)
            elif line.startswith('<details>') or line.startswith('<callout') or \
                 line.startswith('<table') or line.startswith('<columns'):
                # For now, convert to paragraph with preserved XML
                # TODO: Parse and convert back to Notion blocks
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": line}}]
                    }
                })
                i += 1

            # Default: paragraph
            else:
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": line}}]
                    }
                })
                i += 1

        return blocks

    # Public API methods

    def fetch_page(self, page_id: str) -> Dict[str, Any]:
        """
        Fetch page content as markdown

        Args:
            page_id: Notion page ID or URL

        Returns:
            Dictionary with:
            - id: Page ID
            - title: Page title
            - content: Markdown content (body only, no title)
            - parent_title: Parent page title (if available)
            - blocks: Raw block data

        Raises:
            NotionAPIError: On API errors
            ValueError: On invalid page ID
        """
        page = self._get_page(page_id)
        blocks = self._get_blocks(page["id"])

        title = self._extract_title(page)
        parent_title = self._get_parent_title(page)
        content = self._blocks_to_markdown(blocks)

        return {
            "id": page["id"],
            "title": title,
            "content": content.strip(),
            "parent_title": parent_title,
            "blocks": blocks
        }

    def create_page(self, title: str, content: str, parent_id: Optional[str] = None) -> Dict[str, str]:
        """
        Create a new page

        Args:
            title: Page title
            content: Markdown content
            parent_id: Parent page ID (optional, uses workspace if None)

        Returns:
            Dictionary with:
            - id: Created page ID
            - url: Page URL

        Raises:
            NotionAPIError: On API errors
        """
        # Build parent reference
        parent = {}
        if parent_id:
            parent_id = self._clean_id(parent_id)
            parent = {"type": "page_id", "page_id": parent_id}
        else:
            # Default to workspace (will fail if no access, user must provide parent)
            raise ValueError("parent_id is required - provide a parent page ID")

        # Build page properties with title
        properties = {
            "title": {
                "title": [
                    {
                        "type": "text",
                        "text": {"content": title}
                    }
                ]
            }
        }

        # Convert markdown to blocks
        blocks = self._markdown_to_blocks(content)

        # Limit to 100 blocks (API limit for create)
        if len(blocks) > 100:
            blocks = blocks[:100]

        # Create page
        response = self._request("POST", "/pages", {
            "parent": parent,
            "properties": properties,
            "children": blocks
        })

        return {
            "id": response["id"],
            "url": response["url"]
        }

    def update_page(self, page_id: str, content: str) -> Dict[str, Any]:
        """
        Update page content

        Strategy: Delete all existing blocks (except child pages), then append new blocks

        Args:
            page_id: Notion page ID
            content: New markdown content

        Returns:
            Dictionary with:
            - id: Page ID
            - success: True if successful

        Raises:
            NotionAPIError: On API errors
        """
        page_id = self._clean_id(page_id)

        # Get existing blocks
        existing_blocks = self._get_blocks(page_id)

        # Delete all non-child-page blocks
        for block in existing_blocks:
            # Keep child pages (they're separate pages, not content)
            if block.get("type") == "child_page":
                continue
            try:
                self._delete_block(block["id"])
            except NotionAPIError as e:
                # Continue even if delete fails (block might already be gone)
                print(f"Warning: Could not delete block {block['id']}: {e}")

        # Convert new content to blocks
        new_blocks = self._markdown_to_blocks(content)

        # Append new blocks in batches (API limit: 100 blocks per request)
        batch_size = 100
        for i in range(0, len(new_blocks), batch_size):
            batch = new_blocks[i:i + batch_size]
            self._append_blocks(page_id, batch)

        return {
            "id": page_id,
            "success": True
        }

    def search(self, query: str, filter_type: Optional[str] = None) -> Dict[str, List[Dict]]:
        """
        Search workspace

        Args:
            query: Search query string
            filter_type: Filter by "page" or "database" (optional)

        Returns:
            Dictionary with:
            - results: List of search results, each with:
                - id: Page/database ID
                - title: Title
                - url: URL
                - type: "page" or "database"

        Raises:
            NotionAPIError: On API errors
        """
        payload = {"query": query}

        if filter_type:
            if filter_type not in ["page", "database"]:
                raise ValueError("filter_type must be 'page' or 'database'")
            payload["filter"] = {"property": "object", "value": filter_type}

        response = self._request("POST", "/search", payload)

        results = []
        for item in response.get("results", []):
            obj_type = item.get("object")
            title = self._extract_title(item) if obj_type == "page" else \
                    item.get("title", [{}])[0].get("plain_text", "Untitled")

            results.append({
                "id": item["id"],
                "title": title,
                "url": item["url"],
                "type": obj_type
            })

        return {"results": results}


# Convenience function for command-line usage
def main():
    """Command-line interface for testing"""
    import sys
    import os

    if len(sys.argv) < 3:
        print("Usage: python notion_api.py <api_key> <command> [args...]")
        print("\nCommands:")
        print("  fetch <page_id>           - Fetch page content")
        print("  search <query>            - Search workspace")
        print("  create <title> <content> <parent_id> - Create page")
        print("  update <page_id> <content> - Update page")
        sys.exit(1)

    api_key = sys.argv[1]
    command = sys.argv[2]

    client = NotionAPIClient(api_key)

    try:
        if command == "fetch":
            page_id = sys.argv[3]
            result = client.fetch_page(page_id)
            print(f"Title: {result['title']}")
            print(f"Parent: {result['parent_title']}")
            print(f"\n{result['content']}")

        elif command == "search":
            query = sys.argv[3]
            result = client.search(query)
            for item in result['results']:
                print(f"{item['type']}: {item['title']} ({item['id']})")

        elif command == "create":
            title = sys.argv[3]
            content = sys.argv[4]
            parent_id = sys.argv[5]
            result = client.create_page(title, content, parent_id)
            print(f"Created: {result['url']}")

        elif command == "update":
            page_id = sys.argv[3]
            content = sys.argv[4]
            result = client.update_page(page_id, content)
            print(f"Updated page {result['id']}")

        else:
            print(f"Unknown command: {command}")
            sys.exit(1)

    except (NotionAPIError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
