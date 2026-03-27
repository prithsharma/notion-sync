#!/usr/bin/env python3
"""
Main NotionSync orchestrator class.

This module provides the high-level API for notion-sync operations,
coordinating between the API client, manifest manager, frontmatter parser,
and hashing utilities.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

# Handle both package import and direct execution
if __name__ == "__main__" and __package__ is None:
    # Direct execution: add parent directory to path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from lib.notion_api import NotionAPIClient, NotionAPIError
    from lib.manifest import ManifestManager
    from lib.frontmatter import FrontmatterParser
    from lib.hashing import compute_hash
else:
    # Package import: use relative imports
    from .notion_api import NotionAPIClient, NotionAPIError
    from .manifest import ManifestManager
    from .frontmatter import FrontmatterParser
    from .hashing import compute_hash


# Rich block patterns for detection
RICH_BLOCK_PATTERNS = [
    "<details", "<callout", "<table",
    "<columns", "<synced_block", "<meeting-notes"
]


class NotionSync:
    """
    Main orchestrator for notion-sync operations.

    Coordinates pull, push, status, fetch, and search operations
    by combining the NotionAPIClient, ManifestManager, FrontmatterParser,
    and hashing utilities.
    """

    def __init__(self, sync_dir: Optional[str] = None):
        """
        Initialize NotionSync with sync directory.

        Args:
            sync_dir: Directory for sync state (default: ~/.notion-sync)
        """
        if sync_dir is None:
            sync_dir = Path.home() / ".notion-sync"

        self.sync_dir = Path(sync_dir)
        self.sync_dir.mkdir(parents=True, exist_ok=True)

        # Initialize manifest manager
        self.manifest_path = self.sync_dir / "manifest.json"
        self.manifest = ManifestManager(self.manifest_path)

        # Blocks directory for rich blocks
        self.blocks_dir = self.sync_dir / "blocks"
        self.blocks_dir.mkdir(parents=True, exist_ok=True)

        # API client (lazy initialized)
        self._api_client = None

    def _get_api_client(self, token: Optional[str] = None) -> NotionAPIClient:
        """
        Get or create API client (lazy initialization).

        Args:
            token: Notion API token (if None, tries env var)

        Returns:
            NotionAPIClient instance

        Raises:
            ValueError: If no token provided and NOTION_API_KEY not set
        """
        # Use provided token or env var
        if token is None:
            token = os.environ.get("NOTION_API_KEY")

        if not token:
            raise ValueError(
                "Notion API key required. Provide --notion-token or set NOTION_API_KEY env var."
            )

        # Create new client if token changed or not initialized
        if self._api_client is None or self._api_client.api_key != token:
            self._api_client = NotionAPIClient(token)

        return self._api_client

    def _detect_rich_blocks(self, content: str) -> bool:
        """
        Check if content contains rich blocks.

        Args:
            content: Markdown content

        Returns:
            True if content has rich blocks
        """
        return any(pattern in content for pattern in RICH_BLOCK_PATTERNS)

    def _parse_pull_args(self, args: List[str]) -> Tuple[str, str, Optional[str]]:
        """
        Parse pull command arguments.

        Args:
            args: List of command arguments

        Returns:
            Tuple of (page_id, output_path, token)

        Raises:
            ValueError: If required arguments missing
        """
        if len(args) < 2:
            raise ValueError("Usage: pull <page_id> <output_path> [--notion-token TOKEN]")

        page_id = args[0]
        output_path = args[1]
        token = None

        # Parse optional flags
        i = 2
        while i < len(args):
            if args[i] in ["--notion-token", "-t"] and i + 1 < len(args):
                token = args[i + 1]
                i += 2
            else:
                i += 1

        return page_id, output_path, token

    def _parse_push_args(self, args: List[str]) -> Tuple[str, bool, Optional[str], Optional[str]]:
        """
        Parse push command arguments.

        Args:
            args: List of command arguments

        Returns:
            Tuple of (file_path, force, token, parent_id)

        Raises:
            ValueError: If required arguments missing
        """
        if len(args) < 1:
            raise ValueError("Usage: push <file_path> [--force] [--notion-token TOKEN] [--parent-id ID]")

        file_path = args[0]
        force = False
        token = None
        parent_id = None

        # Parse optional flags
        i = 1
        while i < len(args):
            if args[i] in ["--force", "-f"]:
                force = True
                i += 1
            elif args[i] in ["--notion-token", "-t"] and i + 1 < len(args):
                token = args[i + 1]
                i += 2
            elif args[i] in ["--parent-id", "-p"] and i + 1 < len(args):
                parent_id = args[i + 1]
                i += 2
            else:
                i += 1

        return file_path, force, token, parent_id

    def _parse_status_args(self, args: List[str]) -> Tuple[Optional[str], bool]:
        """
        Parse status command arguments.

        Args:
            args: List of command arguments

        Returns:
            Tuple of (file_path or None for all, verbose)
        """
        file_path = None
        verbose = False

        i = 0
        while i < len(args):
            if args[i] in ["--verbose", "-v"]:
                verbose = True
                i += 1
            elif not args[i].startswith("-"):
                file_path = args[i]
                i += 1
            else:
                i += 1

        return file_path, verbose

    def _parse_fetch_args(self, args: List[str]) -> Tuple[str, Optional[str]]:
        """
        Parse fetch command arguments.

        Args:
            args: List of command arguments

        Returns:
            Tuple of (page_id, token)

        Raises:
            ValueError: If required arguments missing
        """
        if len(args) < 1:
            raise ValueError("Usage: fetch <page_id> [--notion-token TOKEN]")

        page_id = args[0]
        token = None

        # Parse optional flags
        i = 1
        while i < len(args):
            if args[i] in ["--notion-token", "-t"] and i + 1 < len(args):
                token = args[i + 1]
                i += 2
            else:
                i += 1

        return page_id, token

    def _parse_search_args(self, args: List[str]) -> Tuple[str, Optional[str], Optional[str]]:
        """
        Parse search command arguments.

        Args:
            args: List of command arguments

        Returns:
            Tuple of (query, token, filter_type)

        Raises:
            ValueError: If required arguments missing
        """
        if len(args) < 1:
            raise ValueError("Usage: search <query> [--notion-token TOKEN] [--type page|database]")

        query = args[0]
        token = None
        filter_type = None

        # Parse optional flags
        i = 1
        while i < len(args):
            if args[i] in ["--notion-token", "-t"] and i + 1 < len(args):
                token = args[i + 1]
                i += 2
            elif args[i] in ["--type"] and i + 1 < len(args):
                filter_type = args[i + 1]
                i += 2
            else:
                i += 1

        return query, token, filter_type

    def _get_file_status(self, file_path: str, verbose: bool = False) -> Dict[str, Any]:
        """
        Get sync status for a single file.

        Args:
            file_path: Path to the file
            verbose: Include detailed information

        Returns:
            Dictionary with status information
        """
        entry = self.manifest.get_entry(file_path)

        if entry is None:
            return {
                "path": file_path,
                "status": "not_synced",
                "notion_id": None,
                "last_synced": None
            }

        # Check if file exists
        path = Path(file_path)
        if not path.exists():
            return {
                "path": file_path,
                "status": "not_found",
                "notion_id": entry.get("notion_id"),
                "last_synced": entry.get("last_synced")
            }

        # Read current content and compute hash
        try:
            content = path.read_text(encoding='utf-8')
            frontmatter, body = FrontmatterParser.parse(content)
            current_hash = compute_hash(body)

            manifest_hash = entry.get("local_hash")

            # Compare hashes
            if current_hash == manifest_hash:
                status = "synced"
            else:
                status = "local_modified"

            result = {
                "path": file_path,
                "status": status,
                "notion_id": entry.get("notion_id"),
                "last_synced": entry.get("last_synced")
            }

            if verbose:
                result["hashes"] = {
                    "current": current_hash,
                    "manifest": manifest_hash,
                    "notion_at_sync": entry.get("notion_hash_at_sync")
                }

            return result

        except Exception as e:
            return {
                "path": file_path,
                "status": "error",
                "error": str(e),
                "notion_id": entry.get("notion_id")
            }

    def pull(self, args: List[str]) -> Dict[str, Any]:
        """
        Pull Notion page to local file.

        Args:
            args: Command arguments [page_id, output_path, --notion-token, TOKEN]

        Returns:
            JSON dict with {success, file_path, notion_id, title, has_rich_blocks, hashes}
            or {error, type} on failure
        """
        try:
            # Parse arguments
            page_id, output_path, token = self._parse_pull_args(args)

            # Get API client
            api = self._get_api_client(token)

            # Clean page ID
            page_id = api._clean_id(page_id)

            # Check if already synced elsewhere
            existing = self.manifest.find_by_notion_id(page_id)
            if existing and existing["file_path"] != output_path:
                return {
                    "error": f"Page already synced to: {existing['file_path']}",
                    "type": "already_synced",
                    "existing_path": existing["file_path"]
                }

            # Fetch from Notion
            page_data = api.fetch_page(page_id)

            title = page_data["title"]
            content = page_data["content"]
            parent_title = page_data.get("parent_title")
            blocks = page_data["blocks"]

            # Detect rich blocks
            has_rich_blocks = self._detect_rich_blocks(content)

            # Build frontmatter
            frontmatter = {
                "notion_id": page_id,
                "title": title,
                "synced_at": datetime.utcnow().isoformat() + "Z"
            }

            if parent_title:
                frontmatter["parent"] = parent_title

            if has_rich_blocks:
                frontmatter["has_rich_blocks"] = True

            # Combine frontmatter and content
            full_content = FrontmatterParser.serialize(frontmatter, content)

            # Write file
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(full_content, encoding='utf-8')

            # Save raw blocks if has rich blocks
            if has_rich_blocks:
                blocks_file = self.blocks_dir / f"{page_id}.json"
                blocks_file.write_text(json.dumps(blocks, indent=2), encoding='utf-8')

            # Compute hashes
            content_hash = compute_hash(content)

            # Update manifest
            self.manifest.update_entry(output_path, {
                "notion_id": page_id,
                "last_synced": frontmatter["synced_at"],
                "local_hash": content_hash,
                "notion_hash": content_hash,
                "notion_hash_at_sync": content_hash
            })

            return {
                "success": True,
                "file_path": output_path,
                "notion_id": page_id,
                "title": title,
                "has_rich_blocks": has_rich_blocks,
                "hashes": {
                    "local": content_hash,
                    "notion": content_hash
                }
            }

        except ValueError as e:
            return {"error": str(e), "type": "ValueError"}
        except NotionAPIError as e:
            return {"error": str(e), "type": "NotionAPIError"}
        except Exception as e:
            return {"error": str(e), "type": type(e).__name__}

    def push(self, args: List[str]) -> Dict[str, Any]:
        """
        Push local file to Notion.

        Args:
            args: Command arguments [file_path, --force, --notion-token, TOKEN, --parent-id, ID]

        Returns:
            JSON dict with {success, operation, notion_id, notion_url, conflict}
            or {error, type} on failure
        """
        try:
            # Parse arguments
            file_path, force, token, parent_id = self._parse_push_args(args)

            # Check file exists
            path = Path(file_path)
            if not path.exists():
                return {"error": f"File not found: {file_path}", "type": "not_found"}

            # Read file
            content = path.read_text(encoding='utf-8')
            frontmatter, body = FrontmatterParser.parse(content)

            # Get API client
            api = self._get_api_client(token)

            # Get manifest entry
            entry = self.manifest.get_entry(file_path)
            notion_id = frontmatter.get("notion_id") or (entry.get("notion_id") if entry else None)

            # Determine operation: create vs update
            if notion_id:
                operation = "update"

                # Clean notion ID
                notion_id = api._clean_id(notion_id)

                # Detect conflicts (3-way hash comparison)
                local_hash = compute_hash(body)
                manifest_local = entry.get("local_hash") if entry else None
                baseline_notion = entry.get("notion_hash_at_sync") if entry else None

                local_changed = local_hash != manifest_local

                # Fetch current Notion content to check if it changed
                if local_changed and baseline_notion and not force:
                    try:
                        current_notion = api.fetch_page(notion_id)
                        current_notion_hash = compute_hash(current_notion["content"])
                        notion_changed = current_notion_hash != baseline_notion

                        if notion_changed:
                            # CONFLICT!
                            return {
                                "success": False,
                                "conflict": {
                                    "local_content": body,
                                    "notion_content": current_notion["content"],
                                    "local_hash": local_hash,
                                    "notion_hash": current_notion_hash,
                                    "baseline_hash": baseline_notion,
                                    "message": "Both local and Notion have changes. Use --force to overwrite Notion."
                                }
                            }
                    except NotionAPIError:
                        # If we can't fetch, proceed with push
                        pass

                # Update page
                result = api.update_page(notion_id, body)
                notion_url = f"https://notion.so/{notion_id.replace('-', '')}"

            else:
                operation = "create"

                # Need parent ID for creation
                if not parent_id:
                    return {
                        "error": "Parent ID required for creating new pages. Use --parent-id",
                        "type": "missing_parent"
                    }

                # Extract title from frontmatter or first heading
                title = frontmatter.get("title")
                if not title:
                    # Try to extract from first line
                    first_line = body.split('\n')[0].strip()
                    if first_line.startswith('#'):
                        title = first_line.lstrip('#').strip()
                    else:
                        title = "Untitled"

                # Create page
                result = api.create_page(title, body, parent_id)
                notion_id = result["id"]
                notion_url = result["url"]

                # Update frontmatter with notion_id
                frontmatter["notion_id"] = notion_id
                frontmatter["title"] = title

                # Write back to file with updated frontmatter
                updated_content = FrontmatterParser.serialize(frontmatter, body)
                path.write_text(updated_content, encoding='utf-8')

            # Compute new hashes
            content_hash = compute_hash(body)

            # Update manifest
            self.manifest.update_entry(file_path, {
                "notion_id": notion_id,
                "last_synced": datetime.utcnow().isoformat() + "Z",
                "local_hash": content_hash,
                "notion_hash": content_hash,
                "notion_hash_at_sync": content_hash
            })

            return {
                "success": True,
                "operation": operation,
                "notion_id": notion_id,
                "notion_url": notion_url
            }

        except ValueError as e:
            return {"error": str(e), "type": "ValueError"}
        except NotionAPIError as e:
            return {"error": str(e), "type": "NotionAPIError"}
        except Exception as e:
            return {"error": str(e), "type": type(e).__name__}

    def status(self, args: List[str]) -> Dict[str, Any]:
        """
        Get sync status for files.

        Args:
            args: Command arguments [[file_path], --verbose]

        Returns:
            JSON dict with {files: [{path, status, notion_id, last_synced, hashes}]}
            or {error, type} on failure
        """
        try:
            # Parse arguments
            file_path, verbose = self._parse_status_args(args)

            files = []

            if file_path:
                # Status for single file
                status_info = self._get_file_status(file_path, verbose)
                files.append(status_info)
            else:
                # Status for all files in manifest
                all_entries = self.manifest.list_all()
                for entry in all_entries:
                    status_info = self._get_file_status(entry["file_path"], verbose)
                    files.append(status_info)

            return {"files": files}

        except Exception as e:
            return {"error": str(e), "type": type(e).__name__}

    def fetch_page(self, args: List[str]) -> Dict[str, Any]:
        """
        Fetch page metadata without saving.

        Args:
            args: Command arguments [page_id, --notion-token, TOKEN]

        Returns:
            JSON dict with {page_id, title, content, parent_title}
            or {error, type} on failure
        """
        try:
            # Parse arguments
            page_id, token = self._parse_fetch_args(args)

            # Get API client
            api = self._get_api_client(token)

            # Fetch page
            page_data = api.fetch_page(page_id)

            return {
                "page_id": page_data["id"],
                "title": page_data["title"],
                "content": page_data["content"],
                "parent_title": page_data.get("parent_title")
            }

        except ValueError as e:
            return {"error": str(e), "type": "ValueError"}
        except NotionAPIError as e:
            return {"error": str(e), "type": "NotionAPIError"}
        except Exception as e:
            return {"error": str(e), "type": type(e).__name__}

    def search(self, args: List[str]) -> Dict[str, Any]:
        """
        Search Notion workspace.

        Args:
            args: Command arguments [query, --notion-token, TOKEN, --type, page|database]

        Returns:
            JSON dict with {results: [{id, title, url, type}]}
            or {error, type} on failure
        """
        try:
            # Parse arguments
            query, token, filter_type = self._parse_search_args(args)

            # Get API client
            api = self._get_api_client(token)

            # Search
            results = api.search(query, filter_type)

            return results

        except ValueError as e:
            return {"error": str(e), "type": "ValueError"}
        except NotionAPIError as e:
            return {"error": str(e), "type": "NotionAPIError"}
        except Exception as e:
            return {"error": str(e), "type": type(e).__name__}


# CLI entry point for testing
def main():
    """Command-line interface for testing"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python notion_sync.py <command> [args...]")
        print("\nCommands:")
        print("  pull <page_id> <output_path> [--notion-token TOKEN]")
        print("  push <file_path> [--force] [--notion-token TOKEN] [--parent-id ID]")
        print("  status [file_path] [--verbose]")
        print("  fetch <page_id> [--notion-token TOKEN]")
        print("  search <query> [--notion-token TOKEN] [--type page|database]")
        sys.exit(1)

    command = sys.argv[1]
    args = sys.argv[2:]

    sync = NotionSync()

    # Route to appropriate method
    if command == "pull":
        result = sync.pull(args)
    elif command == "push":
        result = sync.push(args)
    elif command == "status":
        result = sync.status(args)
    elif command == "fetch":
        result = sync.fetch_page(args)
    elif command == "search":
        result = sync.search(args)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

    # Print result as JSON
    print(json.dumps(result, indent=2))

    # Exit with error code if operation failed
    if not result.get("success", True) or "error" in result:
        sys.exit(1)


if __name__ == "__main__":
    main()
