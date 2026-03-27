# NotionSync Orchestrator Class

The main Python class that coordinates all notion-sync operations.

## Overview

`NotionSync` is the heart of the Python backend. It ties together:
- **NotionAPIClient** - REST API communication
- **ManifestManager** - Sync state tracking
- **FrontmatterParser** - YAML frontmatter handling
- **Hashing utilities** - Content change detection

## Installation

```python
from lib.notion_sync import NotionSync

# Initialize with default sync directory (~/.notion-sync)
sync = NotionSync()

# Or specify custom sync directory
sync = NotionSync("/path/to/sync-dir")
```

## API Reference

### Constructor

```python
NotionSync(sync_dir: Optional[str] = None)
```

**Args:**
- `sync_dir` - Directory for sync state (default: `~/.notion-sync`)

**Creates:**
- `manifest.json` - Sync state tracker
- `blocks/` - Directory for raw block data

---

### pull()

Pull a Notion page to local markdown file.

```python
result = sync.pull([page_id, output_path, "--notion-token", token])
```

**Args:**
- `page_id` - Notion page ID or URL
- `output_path` - Local file path to save
- `--notion-token` (optional) - Notion API key
- `-t` (alias for --notion-token)

**Returns:**
```json
{
  "success": true,
  "file_path": "docs/page.md",
  "notion_id": "abc123...",
  "title": "Page Title",
  "has_rich_blocks": false,
  "hashes": {
    "local": "sha256...",
    "notion": "sha256..."
  }
}
```

**Error Response:**
```json
{
  "error": "Error message",
  "type": "ValueError|NotionAPIError|..."
}
```

**Conflict Response:**
```json
{
  "error": "Page already synced to: other/file.md",
  "type": "already_synced",
  "existing_path": "other/file.md"
}
```

**Example:**
```python
# Pull with token from environment
result = sync.pull(["abc123", "docs/page.md"])

# Pull with explicit token
result = sync.pull([
    "https://notion.so/Page-Title-abc123",
    "docs/page.md",
    "--notion-token", "secret_xxx"
])
```

**Behavior:**
1. Fetches page from Notion API
2. Converts blocks to markdown
3. Detects rich blocks (toggle, callout, table)
4. Builds frontmatter with metadata
5. Writes file with frontmatter + content
6. Saves raw blocks to `blocks/` if has rich blocks
7. Computes hashes for change detection
8. Updates manifest with sync state

---

### push()

Push local markdown file to Notion.

```python
result = sync.push([file_path, "--force", "--notion-token", token, "--parent-id", parent])
```

**Args:**
- `file_path` - Local markdown file path
- `--force` (optional) - Overwrite Notion changes without conflict check
- `-f` (alias for --force)
- `--notion-token` (optional) - Notion API key
- `-t` (alias for --notion-token)
- `--parent-id` (optional) - Parent page ID for new pages
- `-p` (alias for --parent-id)

**Returns (Update):**
```json
{
  "success": true,
  "operation": "update",
  "notion_id": "abc123...",
  "notion_url": "https://notion.so/abc123..."
}
```

**Returns (Create):**
```json
{
  "success": true,
  "operation": "create",
  "notion_id": "abc123...",
  "notion_url": "https://notion.so/abc123..."
}
```

**Conflict Response:**
```json
{
  "success": false,
  "conflict": {
    "local_content": "# Local version\n...",
    "notion_content": "# Notion version\n...",
    "local_hash": "sha256...",
    "notion_hash": "sha256...",
    "baseline_hash": "sha256...",
    "message": "Both local and Notion have changes. Use --force to overwrite Notion."
  }
}
```

**Example:**
```python
# Update existing page
result = sync.push(["docs/page.md"])

# Create new page
result = sync.push([
    "docs/new-page.md",
    "--parent-id", "parent123"
])

# Force push (ignore conflicts)
result = sync.push([
    "docs/page.md",
    "--force"
])
```

**Behavior:**

**For updates (notion_id exists):**
1. Reads local file and parses frontmatter
2. Detects conflicts using 3-way hash comparison:
   - `local_hash != manifest_local` → local changed
   - `notion_hash != baseline_notion` → Notion changed
   - Both changed → **CONFLICT** (unless `--force`)
3. Updates page via Notion API
4. Updates manifest with new hashes

**For creates (no notion_id):**
1. Requires `--parent-id` for parent page
2. Extracts title from frontmatter or first heading
3. Creates new page via Notion API
4. Adds `notion_id` to frontmatter
5. Updates local file with new frontmatter
6. Updates manifest

---

### status()

Get sync status for tracked files.

```python
result = sync.status([file_path, "--verbose"])
```

**Args:**
- `file_path` (optional) - Check specific file (default: all)
- `--verbose` (optional) - Include detailed hash information
- `-v` (alias for --verbose)

**Returns:**
```json
{
  "files": [
    {
      "path": "docs/page.md",
      "status": "synced|local_modified|not_found|not_synced",
      "notion_id": "abc123...",
      "last_synced": "2026-03-28T10:30:00Z"
    }
  ]
}
```

**With --verbose:**
```json
{
  "files": [
    {
      "path": "docs/page.md",
      "status": "synced",
      "notion_id": "abc123...",
      "last_synced": "2026-03-28T10:30:00Z",
      "hashes": {
        "current": "sha256...",
        "manifest": "sha256...",
        "notion_at_sync": "sha256..."
      }
    }
  ]
}
```

**Status Values:**
- `synced` - File matches manifest (in sync)
- `local_modified` - Local changes not pushed
- `not_found` - File in manifest but missing locally
- `not_synced` - File not tracked in manifest
- `error` - Error reading file

**Example:**
```python
# Check all files
result = sync.status([])

# Check specific file
result = sync.status(["docs/page.md"])

# Verbose output
result = sync.status(["docs/page.md", "--verbose"])
```

---

### fetch_page()

Fetch page metadata without saving to file.

```python
result = sync.fetch_page([page_id, "--notion-token", token])
```

**Args:**
- `page_id` - Notion page ID or URL
- `--notion-token` (optional) - Notion API key

**Returns:**
```json
{
  "page_id": "abc123...",
  "title": "Page Title",
  "content": "# Markdown content\n...",
  "parent_title": "Parent Page"
}
```

**Example:**
```python
# Fetch page metadata
result = sync.fetch_page(["abc123"])

# Check what's on a page without pulling
if result.get("title") == "Meeting Notes":
    print("This is a meeting notes page")
```

---

### search()

Search Notion workspace.

```python
result = sync.search([query, "--notion-token", token, "--type", page_type])
```

**Args:**
- `query` - Search query string
- `--notion-token` (optional) - Notion API key
- `--type` (optional) - Filter by "page" or "database"

**Returns:**
```json
{
  "results": [
    {
      "id": "abc123...",
      "title": "Page Title",
      "url": "https://notion.so/...",
      "type": "page"
    }
  ]
}
```

**Example:**
```python
# Search all
result = sync.search(["meeting notes"])

# Search pages only
result = sync.search([
    "architecture",
    "--type", "page"
])

# List results
for item in result["results"]:
    print(f"{item['title']}: {item['url']}")
```

---

## Token Management

Notion API token is resolved in this order:

1. **Explicit flag**: `--notion-token SECRET`
2. **Environment variable**: `NOTION_API_KEY=SECRET`
3. **Error**: If neither provided

**Best Practices:**

```bash
# Set environment variable
export NOTION_API_KEY="secret_xxx"

# Or store in .env file
echo "NOTION_API_KEY=secret_xxx" >> .env
source .env
```

---

## Conflict Detection

The push operation uses **3-way hash comparison** to detect conflicts:

```
Baseline (at last sync) ──┬──> Local (current)
                          │
                          └──> Notion (current)
```

**Scenarios:**

1. **No conflict** (local changed, Notion unchanged):
   - Push proceeds normally
   - Notion gets overwritten

2. **No conflict** (local unchanged, Notion changed):
   - User likely wants to pull first
   - But push still proceeds (creates duplicate)

3. **CONFLICT** (both changed):
   - Push fails with conflict details
   - User must resolve manually or use `--force`

**Resolution:**

```python
# Option 1: Force push (overwrite Notion)
result = sync.push(["docs/page.md", "--force"])

# Option 2: Pull first (overwrite local)
result = sync.pull(["abc123", "docs/page.md"])

# Option 3: Manual merge
conflict = result["conflict"]
# Compare conflict["local_content"] vs conflict["notion_content"]
# Merge manually, then push with --force
```

---

## Rich Blocks

Rich blocks (toggle, callout, table) are preserved during sync:

**Detection:**
- `<details>` - Toggle blocks
- `<callout>` - Callout blocks
- `<table>` - Tables
- `<columns>` - Column layouts
- `<synced_block>` - Synced blocks

**Storage:**
- Raw block JSON saved to `blocks/{page_id}.json`
- Used for round-trip conversion back to Notion
- Frontmatter includes `has_rich_blocks: true`

**Limitations:**
- Rich blocks are preserved as XML tags in markdown
- Round-trip conversion is lossy (Notion → Markdown → Notion)
- Complex nested structures may not convert perfectly

---

## File Structure

```
~/.notion-sync/
├── manifest.json          # Sync state tracker
└── blocks/
    ├── abc123.json       # Raw blocks for page abc123
    └── def456.json       # Raw blocks for page def456
```

**manifest.json:**
```json
{
  "default_database": null,
  "files": {
    "docs/page.md": {
      "notion_id": "abc123",
      "last_synced": "2026-03-28T10:30:00Z",
      "local_hash": "sha256...",
      "notion_hash": "sha256...",
      "notion_hash_at_sync": "sha256..."
    }
  }
}
```

**Frontmatter (in markdown files):**
```yaml
---
notion_id: abc123-def4-5678-90ab-cdef12345678
title: Page Title
synced_at: 2026-03-28T10:30:00Z
parent: Parent Page
has_rich_blocks: true
---

# Page content here
```

---

## CLI Usage

The module can be run directly for testing:

```bash
# Pull a page
python3 lib/notion_sync.py pull abc123 docs/page.md --notion-token secret_xxx

# Push a file
python3 lib/notion_sync.py push docs/page.md --force

# Check status
python3 lib/notion_sync.py status docs/page.md --verbose

# Fetch page metadata
python3 lib/notion_sync.py fetch abc123

# Search workspace
python3 lib/notion_sync.py search "meeting notes" --type page
```

**Output:** All commands return JSON to stdout.

---

## Error Handling

All methods return structured error dictionaries:

```json
{
  "error": "Error message",
  "type": "ValueError|NotionAPIError|FileNotFoundError|..."
}
```

**Common Errors:**

- `ValueError` - Invalid arguments
- `NotionAPIError` - Notion API failures
- `FileNotFoundError` - File not found
- `already_synced` - Page synced to different file
- `missing_parent` - Parent ID required for creation
- `not_found` - File not found

**Example:**
```python
result = sync.pull(["invalid", "out.md"])
if "error" in result:
    print(f"Error: {result['error']}")
    print(f"Type: {result['type']}")
```

---

## Testing

Run the test suite:

```bash
python3 test_notion_sync.py
```

**Tests:**
- Initialization
- Status operations (empty and with files)
- Rich block detection
- Argument parsing for all commands
- Error handling
- Frontmatter integration
- Manifest integration

---

## Integration with CLI

The NotionSync class is designed to be called from bash/Node.js CLI:

**From Bash:**
```bash
#!/bin/bash
python3 -c "
from lib.notion_sync import NotionSync
import sys
sync = NotionSync()
result = sync.pull(sys.argv[1:])
print(result)
" "$@"
```

**From Node.js:**
```javascript
const { execSync } = require('child_process');
const result = JSON.parse(execSync(
  'python3 -c "from lib.notion_sync import NotionSync; ...',
  { encoding: 'utf-8' }
));
```

---

## Next Steps

1. **Skills Integration**: Update `/pull-notion`, `/push-notion`, `/notion-status` skills to use NotionSync
2. **CLI Wrapper**: Create `notion-sync` bash wrapper script
3. **Per-Project State**: Add support for project-specific manifests
4. **Rich Block Round-trip**: Improve Markdown → Notion conversion for rich blocks
5. **Batch Operations**: Add bulk pull/push support

---

## See Also

- [Notion API Client](../lib/README.md#notion_apipy) - REST API wrapper
- [Manifest Manager](../lib/README.md#manifestpy) - Sync state tracking
- [Frontmatter Parser](../lib/README.md#frontmatterpy) - YAML handling
- [Per-Project State](./per-project-state.md) - Project-specific sync
