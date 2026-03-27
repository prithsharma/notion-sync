#!/usr/bin/env python3
"""
Example: How to integrate NotionSync with CLI skills

This shows how the /pull-notion, /push-notion, and /notion-status
skills can use the NotionSync orchestrator class.
"""

import sys
import json
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.notion_sync import NotionSync


def pull_notion_skill(page_id: str, output_path: str, token: str = None):
    """
    Example: /pull-notion skill implementation

    Usage:
        /pull-notion <page_id> <output_path>
    """
    sync = NotionSync()

    args = [page_id, output_path]
    if token:
        args.extend(["--notion-token", token])

    result = sync.pull(args)

    if result.get("success"):
        print(f"✓ Pulled: {result['title']}")
        print(f"  File: {result['file_path']}")
        print(f"  Notion ID: {result['notion_id']}")
        if result.get("has_rich_blocks"):
            print(f"  ⚠ Contains rich blocks (toggle, callout, etc.)")
        return 0
    else:
        print(f"✗ Error: {result.get('error')}")
        return 1


def push_notion_skill(file_path: str, force: bool = False, token: str = None, parent_id: str = None):
    """
    Example: /push-notion skill implementation

    Usage:
        /push-notion <file_path> [--force]
    """
    sync = NotionSync()

    args = [file_path]
    if force:
        args.append("--force")
    if token:
        args.extend(["--notion-token", token])
    if parent_id:
        args.extend(["--parent-id", parent_id])

    result = sync.push(args)

    if result.get("success"):
        operation = result.get("operation", "update")
        print(f"✓ {operation.title()}d page")
        print(f"  Notion URL: {result['notion_url']}")
        return 0
    elif result.get("conflict"):
        conflict = result["conflict"]
        print("✗ CONFLICT: Both local and Notion have changes")
        print(f"  Local hash: {conflict['local_hash'][:8]}...")
        print(f"  Notion hash: {conflict['notion_hash'][:8]}...")
        print(f"  Baseline hash: {conflict['baseline_hash'][:8]}...")
        print("")
        print("Options:")
        print("  1. Use --force to overwrite Notion")
        print("  2. Pull first to get Notion changes")
        print("  3. Manually merge and push with --force")
        return 1
    else:
        print(f"✗ Error: {result.get('error')}")
        return 1


def notion_status_skill(file_path: str = None, verbose: bool = False):
    """
    Example: /notion-status skill implementation

    Usage:
        /notion-status [file_path] [--verbose]
    """
    sync = NotionSync()

    args = []
    if file_path:
        args.append(file_path)
    if verbose:
        args.append("--verbose")

    result = sync.status(args)

    if "files" in result:
        files = result["files"]

        if not files:
            print("No files synced yet.")
            return 0

        print(f"Sync status for {len(files)} file(s):")
        print("")

        for file in files:
            status = file["status"]
            path = file["path"]

            # Status icon
            if status == "synced":
                icon = "✓"
            elif status == "local_modified":
                icon = "⚠"
            elif status == "not_found":
                icon = "✗"
            else:
                icon = "?"

            print(f"{icon} {path}")
            print(f"  Status: {status}")
            print(f"  Notion ID: {file.get('notion_id', 'N/A')}")
            print(f"  Last synced: {file.get('last_synced', 'N/A')}")

            if verbose and "hashes" in file:
                hashes = file["hashes"]
                print(f"  Current hash: {hashes.get('current', 'N/A')[:8]}...")
                print(f"  Manifest hash: {hashes.get('manifest', 'N/A')[:8]}...")
                print(f"  Notion hash: {hashes.get('notion_at_sync', 'N/A')[:8]}...")

            print("")

        return 0
    else:
        print(f"✗ Error: {result.get('error')}")
        return 1


def main():
    """Demo of skill integration"""
    print("=" * 60)
    print("NotionSync Skill Integration Example")
    print("=" * 60)
    print("")

    # Example 1: Pull
    print("Example 1: Pull a page")
    print("-" * 60)
    print("Command: /pull-notion abc123 docs/page.md")
    print("")
    print("In skill implementation:")
    print("  result = sync.pull(['abc123', 'docs/page.md'])")
    print("")
    print("Expected output:")
    print("  ✓ Pulled: Page Title")
    print("    File: docs/page.md")
    print("    Notion ID: abc123...")
    print("")

    # Example 2: Status
    print("Example 2: Check status")
    print("-" * 60)
    print("Command: /notion-status")
    print("")
    print("In skill implementation:")
    print("  result = sync.status([])")
    print("")
    print("Expected output:")
    print("  Sync status for 1 file(s):")
    print("")
    print("  ✓ docs/page.md")
    print("    Status: synced")
    print("    Notion ID: abc123...")
    print("    Last synced: 2026-03-28T10:30:00Z")
    print("")

    # Example 3: Push
    print("Example 3: Push changes")
    print("-" * 60)
    print("Command: /push-notion docs/page.md")
    print("")
    print("In skill implementation:")
    print("  result = sync.push(['docs/page.md'])")
    print("")
    print("Expected output:")
    print("  ✓ Updated page")
    print("    Notion URL: https://notion.so/abc123...")
    print("")

    # Example 4: Conflict
    print("Example 4: Handle conflict")
    print("-" * 60)
    print("Command: /push-notion docs/page.md")
    print("")
    print("In skill implementation:")
    print("  result = sync.push(['docs/page.md'])")
    print("")
    print("Expected output (on conflict):")
    print("  ✗ CONFLICT: Both local and Notion have changes")
    print("    Local hash: a1b2c3d4...")
    print("    Notion hash: e5f6g7h8...")
    print("    Baseline hash: i9j0k1l2...")
    print("")
    print("  Options:")
    print("    1. Use --force to overwrite Notion")
    print("    2. Pull first to get Notion changes")
    print("    3. Manually merge and push with --force")
    print("")

    print("=" * 60)
    print("Implementation Notes:")
    print("=" * 60)
    print("")
    print("1. Each skill wraps a NotionSync method")
    print("2. Args are passed as list of strings")
    print("3. Results are JSON dictionaries")
    print("4. Skills format output for CLI display")
    print("5. Error handling is built-in")
    print("")
    print("See docs/NOTION_SYNC_CLASS.md for full API reference")
    print("")


if __name__ == "__main__":
    main()
