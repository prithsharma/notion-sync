# Notion Sync Utility Library

Core Python and JavaScript libraries for the notion-sync backend.

## Modules

### notion_api.py
Python REST API client for Notion's API v1. Handles all communication with Notion including fetching, creating, and updating pages.

**Key Features:**
- Fetches pages with full block content
- Converts blocks to Notion-flavored Markdown
- Creates and updates pages
- Search functionality
- Automatic rate limit handling with exponential backoff
- Recursive block fetching with pagination
- Rich block preservation (toggles, callouts, tables)
- Zero external dependencies (stdlib only)

**Class:** `NotionAPIClient`

**Methods:**
- `__init__(api_key: str, rate_limit_retry: bool = True)` - Initialize client
- `fetch_page(page_id: str) -> dict` - Fetch page as markdown
- `create_page(title: str, content: str, parent_id: str) -> dict` - Create new page
- `update_page(page_id: str, content: str) -> dict` - Update page content
- `search(query: str, filter_type: str = None) -> dict` - Search workspace

**Example:**
```python
from lib.notion_api import NotionAPIClient

# Initialize client
client = NotionAPIClient(api_key="secret_xxx")

# Fetch a page
page = client.fetch_page("page-id-or-url")
print(f"Title: {page['title']}")
print(f"Content:\n{page['content']}")

# Create a new page
result = client.create_page(
    title="New Page",
    content="# Hello\n\nThis is my content.",
    parent_id="parent-page-id"
)
print(f"Created: {result['url']}")

# Update a page
client.update_page(
    page_id="page-id",
    content="# Updated\n\nNew content here."
)

# Search
results = client.search("my query", filter_type="page")
for item in results['results']:
    print(f"{item['title']}: {item['url']}")
```

**Block Conversion:**
- Paragraph, Headings (1-3), Lists, Code, Quote, Divider, To-do
- Toggle → `<details><summary>Title</summary>Content</details>`
- Callout → `<callout icon="💡" color="gray">Content</callout>`
- Table → `<table>...</table>` (preserved as XML)
- Child page → `[[Page Name]]`
- Image → `![alt](url)`

**Command-Line Usage:**
```bash
# Fetch a page
python lib/notion_api.py $NOTION_API_KEY fetch <page-id>

# Search
python lib/notion_api.py $NOTION_API_KEY search "query"

# Create a page
python lib/notion_api.py $NOTION_API_KEY create "Title" "Content" <parent-id>

# Update a page
python lib/notion_api.py $NOTION_API_KEY update <page-id> "New content"
```

See `examples/test_notion_api.py` for more usage examples.

---

### hashing.py
SHA-256 hashing utilities for content comparison.

**Functions:**
- `compute_hash(content: str) -> str` - Hash a string
- `hash_file(file_path: str) -> str` - Hash file content

**Example:**
```python
from lib.hashing import compute_hash, hash_file

# Hash string content
hash1 = compute_hash("hello world")

# Hash file content
hash2 = hash_file("path/to/file.md")
```

### frontmatter.py
YAML frontmatter parsing and serialization for markdown files.

**Class:** `FrontmatterParser`

**Methods:**
- `parse(content: str) -> (dict, str)` - Extract frontmatter and body
- `serialize(frontmatter: dict, body: str) -> str` - Combine into markdown

**Example:**
```python
from lib.frontmatter import FrontmatterParser

# Parse markdown with frontmatter
content = """---
title: My Page
notion_id: abc123
---

# Hello World
"""

frontmatter, body = FrontmatterParser.parse(content)
# frontmatter = {'title': 'My Page', 'notion_id': 'abc123'}
# body = '# Hello World'

# Serialize back to markdown
markdown = FrontmatterParser.serialize(frontmatter, body)
```

### manifest.py
Manage manifest.json file for tracking sync state.

**Class:** `ManifestManager`

**Methods:**
- `__init__(manifest_path: Path)` - Initialize with manifest file path
- `read() -> dict` - Read entire manifest
- `write(data: dict)` - Write entire manifest
- `get_entry(file_path: str) -> dict | None` - Get entry for file
- `update_entry(file_path: str, entry: dict)` - Update/create entry
- `remove_entry(file_path: str)` - Remove entry
- `list_all() -> list` - List all entries with file_path included
- `find_by_notion_id(notion_id: str) -> dict | None` - Find by Notion ID
- `get_default_database() -> str | None` - Get default database ID
- `set_default_database(database_id: str | None)` - Set default database ID

**Example:**
```python
from lib.manifest import ManifestManager
from pathlib import Path

# Initialize manager
manager = ManifestManager(Path("manifest.json"))

# Update entry
manager.update_entry("docs/file.md", {
    "notion_id": "abc123",
    "last_synced": "2026-03-28T10:30:00Z",
    "local_hash": "sha256...",
    "notion_hash": "sha256...",
    "notion_hash_at_sync": "sha256..."
})

# Get entry
entry = manager.get_entry("docs/file.md")

# Find by Notion ID
entry = manager.find_by_notion_id("abc123")

# List all entries
all_entries = manager.list_all()
for entry in all_entries:
    print(entry["file_path"], entry["notion_id"])
```

## Manifest Structure

```json
{
  "default_database": "notion_database_id_or_null",
  "files": {
    "path/to/file.md": {
      "notion_id": "abc123",
      "last_synced": "2026-03-28T10:30:00Z",
      "local_hash": "sha256...",
      "notion_hash": "sha256...",
      "notion_hash_at_sync": "sha256..."
    }
  }
}
```

---

### sync-lib.js
JavaScript/Node.js library for sync operations. Handles manifest, frontmatter, hashing, and sync state tracking.

**Key Features:**
- Manifest file operations (read/write/update)
- Frontmatter parsing and serialization (YAML)
- Content hashing (SHA-256) for change detection
- Rich block detection and storage
- Sync status tracking

**Functions:**
```javascript
const syncLib = require('./lib/sync-lib.js');

// Manifest operations
syncLib.readManifest()
syncLib.writeManifest(manifest)
syncLib.getFileEntry(filePath)
syncLib.updateFileEntry(filePath, entry)
syncLib.removeFileEntry(filePath)
syncLib.listSyncedFiles()

// Config operations
syncLib.readConfig()
syncLib.writeConfig(config)

// Frontmatter operations
syncLib.parseFrontmatter(content)
syncLib.serializeFrontmatter(frontmatter)
syncLib.readMarkdownFile(filePath)
syncLib.writeMarkdownFile(filePath, frontmatter, content)

// Hash operations
syncLib.hashContent(content)
syncLib.isLocalModified(filePath)

// Rich block operations
syncLib.hasRichBlocks(content)
syncLib.saveRichBlocks(pageId, blocks)
syncLib.loadRichBlocks(pageId)

// Status operations
syncLib.getSyncStatus(filePath)
syncLib.getAllSyncStatus()
```

**Sync Status Values:**
- `'synced'` - In sync with Notion
- `'local_modified'` - Local changes not pushed
- `'conflict'` - Both local and Notion changed
- `'not_synced'` - Not tracked in manifest
- `'notion_only'` - In manifest but file missing

See [Per-Project State documentation](../docs/per-project-state.md) for details.

---

### hash.sh
Simple shell script for computing SHA-256 hashes.

**Usage:**
```bash
./lib/hash.sh < file.txt
echo "content" | ./lib/hash.sh
```

---

## Package Import

All Python modules can be imported from the `lib` package:

```python
from lib import compute_hash, hash_file, FrontmatterParser, ManifestManager
from lib.notion_api import NotionAPIClient
```

## Dependencies

All modules use only Python standard library:
- `hashlib` - SHA-256 hashing
- `json` - Manifest file handling
- `pathlib` - Path manipulation
- `re` - Regex for frontmatter parsing
- `typing` - Type hints

## Testing

Run the test suite:

```bash
python3 -c "
from lib import compute_hash, FrontmatterParser, ManifestManager
import tempfile
import os

# Test hashing
assert len(compute_hash('test')) == 64
print('✓ Hashing module works')

# Test frontmatter
content = '---\ntitle: Test\n---\n\nBody'
fm, body = FrontmatterParser.parse(content)
assert fm['title'] == 'Test'
assert body == 'Body'
print('✓ Frontmatter module works')

# Test manifest
temp_dir = tempfile.mkdtemp()
manifest_path = os.path.join(temp_dir, 'manifest.json')
manager = ManifestManager(manifest_path)
manager.update_entry('test.md', {'notion_id': '123'})
entry = manager.get_entry('test.md')
assert entry['notion_id'] == '123'
os.unlink(manifest_path)
os.rmdir(temp_dir)
print('✓ Manifest module works')

print('\nAll tests passed!')
"
```
