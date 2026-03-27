#!/usr/bin/env python3
"""
Test script for NotionSync orchestrator.

Tests the complete integration of all components:
- Pull, push, status, fetch, search operations
- Argument parsing
- Manifest management
- Frontmatter handling
- Hash computation
- Conflict detection
"""

import sys
import tempfile
import shutil
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent))

from lib.notion_sync import NotionSync
from lib.frontmatter import FrontmatterParser
from lib.hashing import compute_hash


def test_initialization():
    """Test NotionSync initialization"""
    print("Testing initialization...")

    with tempfile.TemporaryDirectory() as tmpdir:
        sync = NotionSync(tmpdir)

        assert sync.sync_dir == Path(tmpdir)
        assert sync.manifest_path.exists()
        assert sync.blocks_dir.exists()

        print("  ✓ Initialization works")


def test_status_empty():
    """Test status with no files"""
    print("\nTesting status (empty)...")

    with tempfile.TemporaryDirectory() as tmpdir:
        sync = NotionSync(tmpdir)

        result = sync.status([])
        assert "files" in result
        assert result["files"] == []

        print("  ✓ Status works with empty manifest")


def test_status_with_file():
    """Test status with a tracked file"""
    print("\nTesting status (with file)...")

    with tempfile.TemporaryDirectory() as tmpdir:
        sync = NotionSync(tmpdir)

        # Create a test file
        test_file = Path(tmpdir) / "test.md"
        content = "# Test\n\nHello world"
        test_file.write_text(content)

        # Add to manifest
        content_hash = compute_hash(content)
        sync.manifest.update_entry(str(test_file), {
            "notion_id": "abc123",
            "last_synced": "2026-03-28T10:00:00Z",
            "local_hash": content_hash,
            "notion_hash": content_hash,
            "notion_hash_at_sync": content_hash
        })

        # Check status
        result = sync.status([])
        assert len(result["files"]) == 1
        assert result["files"][0]["status"] == "synced"

        print("  ✓ Status reports synced file correctly")

        # Modify file
        test_file.write_text("# Test\n\nModified content")

        result = sync.status([str(test_file)])
        assert result["files"][0]["status"] == "local_modified"

        print("  ✓ Status detects local modifications")


def test_rich_block_detection():
    """Test rich block detection"""
    print("\nTesting rich block detection...")

    with tempfile.TemporaryDirectory() as tmpdir:
        sync = NotionSync(tmpdir)

        # No rich blocks
        assert not sync._detect_rich_blocks("# Normal markdown\n\nParagraph")

        # With rich blocks
        assert sync._detect_rich_blocks("<details>\n<summary>Toggle</summary>\n</details>")
        assert sync._detect_rich_blocks('<callout icon="💡">Note</callout>')
        assert sync._detect_rich_blocks("<table>\n<tr><td>Cell</td></tr>\n</table>")

        print("  ✓ Rich block detection works")


def test_argument_parsing():
    """Test argument parsing for all commands"""
    print("\nTesting argument parsing...")

    with tempfile.TemporaryDirectory() as tmpdir:
        sync = NotionSync(tmpdir)

        # Pull args
        page_id, output, token = sync._parse_pull_args(["abc123", "out.md"])
        assert page_id == "abc123"
        assert output == "out.md"
        assert token is None

        page_id, output, token = sync._parse_pull_args(["abc123", "out.md", "--notion-token", "secret"])
        assert token == "secret"

        print("  ✓ Pull argument parsing works")

        # Push args
        file_path, force, token, parent = sync._parse_push_args(["file.md"])
        assert file_path == "file.md"
        assert force is False
        assert token is None
        assert parent is None

        file_path, force, token, parent = sync._parse_push_args([
            "file.md", "--force", "--notion-token", "secret", "--parent-id", "parent123"
        ])
        assert force is True
        assert token == "secret"
        assert parent == "parent123"

        print("  ✓ Push argument parsing works")

        # Status args
        file_path, verbose = sync._parse_status_args([])
        assert file_path is None
        assert verbose is False

        file_path, verbose = sync._parse_status_args(["file.md", "--verbose"])
        assert file_path == "file.md"
        assert verbose is True

        print("  ✓ Status argument parsing works")

        # Fetch args
        page_id, token = sync._parse_fetch_args(["abc123"])
        assert page_id == "abc123"
        assert token is None

        print("  ✓ Fetch argument parsing works")

        # Search args
        query, token, filter_type = sync._parse_search_args(["test query"])
        assert query == "test query"
        assert token is None
        assert filter_type is None

        query, token, filter_type = sync._parse_search_args([
            "test", "--notion-token", "secret", "--type", "page"
        ])
        assert token == "secret"
        assert filter_type == "page"

        print("  ✓ Search argument parsing works")


def test_error_handling():
    """Test error handling"""
    print("\nTesting error handling...")

    with tempfile.TemporaryDirectory() as tmpdir:
        sync = NotionSync(tmpdir)

        # Missing token
        result = sync.fetch_page(["abc123"])
        assert "error" in result
        assert "API key required" in result["error"]

        print("  ✓ Missing token error handled")

        # Missing file
        result = sync.push(["nonexistent.md"])
        assert "error" in result
        assert "not_found" in result.get("type", "")

        print("  ✓ Missing file error handled")

        # Invalid arguments
        result = sync.pull([])
        assert "error" in result

        print("  ✓ Invalid arguments error handled")


def test_frontmatter_integration():
    """Test frontmatter handling"""
    print("\nTesting frontmatter integration...")

    with tempfile.TemporaryDirectory() as tmpdir:
        sync = NotionSync(tmpdir)

        # Create file with frontmatter
        test_file = Path(tmpdir) / "test.md"
        frontmatter = {
            "notion_id": "abc123",
            "title": "Test Page",
            "synced_at": "2026-03-28T10:00:00Z"
        }
        body = "# Test\n\nContent here"
        content = FrontmatterParser.serialize(frontmatter, body)
        test_file.write_text(content)

        # Parse it back
        parsed_content = test_file.read_text()
        parsed_fm, parsed_body = FrontmatterParser.parse(parsed_content)

        assert parsed_fm["notion_id"] == "abc123"
        assert parsed_fm["title"] == "Test Page"
        assert "Test" in parsed_body

        print("  ✓ Frontmatter integration works")


def test_manifest_integration():
    """Test manifest operations"""
    print("\nTesting manifest integration...")

    with tempfile.TemporaryDirectory() as tmpdir:
        sync = NotionSync(tmpdir)

        # Update entry
        sync.manifest.update_entry("test.md", {
            "notion_id": "abc123",
            "last_synced": "2026-03-28T10:00:00Z",
            "local_hash": "hash1",
            "notion_hash": "hash2",
            "notion_hash_at_sync": "hash3"
        })

        # Get entry
        entry = sync.manifest.get_entry("test.md")
        assert entry["notion_id"] == "abc123"

        # Find by notion ID
        found = sync.manifest.find_by_notion_id("abc123")
        assert found["file_path"] == "test.md"

        # List all
        all_entries = sync.manifest.list_all()
        assert len(all_entries) == 1

        print("  ✓ Manifest integration works")


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("NotionSync Orchestrator Test Suite")
    print("=" * 60)

    try:
        test_initialization()
        test_status_empty()
        test_status_with_file()
        test_rich_block_detection()
        test_argument_parsing()
        test_error_handling()
        test_frontmatter_integration()
        test_manifest_integration()

        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        return 0

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
