# NotionSync Quick Start

Get started with the NotionSync Python backend in 5 minutes.

## Installation

No dependencies required! Uses Python 3.6+ standard library only.

```bash
cd /path/to/notion-sync
export NOTION_API_KEY="secret_xxx"  # Get from https://notion.so/my-integrations
```

## Basic Usage

### Python API

```python
from lib.notion_sync import NotionSync

# Initialize
sync = NotionSync()  # Uses ~/.notion-sync by default

# Pull a page
result = sync.pull(["page-id-or-url", "docs/page.md"])
if result.get("success"):
    print(f"Pulled: {result['title']}")

# Push changes
result = sync.push(["docs/page.md"])
if result.get("success"):
    print(f"Pushed: {result['notion_url']}")

# Check status
result = sync.status([])
for file in result["files"]:
    print(f"{file['path']}: {file['status']}")
```

### Command Line

```bash
# Pull a page
python3 lib/notion_sync.py pull abc123 docs/page.md

# Push changes
python3 lib/notion_sync.py push docs/page.md

# Check status
python3 lib/notion_sync.py status

# Search workspace
python3 lib/notion_sync.py search "meeting notes"
```

## Common Workflows

### Initial Pull

```python
from lib.notion_sync import NotionSync

sync = NotionSync()

# Pull from Notion
result = sync.pull([
    "https://notion.so/My-Page-abc123",
    "docs/my-page.md"
])

print(result)
# {
#   "success": true,
#   "title": "My Page",
#   "file_path": "docs/my-page.md",
#   "notion_id": "abc123..."
# }
```

### Make Changes and Push

```bash
# Edit the file
vim docs/my-page.md

# Check what changed
python3 lib/notion_sync.py status docs/my-page.md
# {"files": [{"path": "docs/my-page.md", "status": "local_modified"}]}

# Push changes
python3 lib/notion_sync.py push docs/my-page.md
# {"success": true, "operation": "update", "notion_url": "..."}
```

### Handle Conflicts

```python
sync = NotionSync()

# Try to push
result = sync.push(["docs/page.md"])

if result.get("conflict"):
    # Both local and Notion changed
    conflict = result["conflict"]

    # Option 1: Force push (overwrite Notion)
    result = sync.push(["docs/page.md", "--force"])

    # Option 2: Pull first (overwrite local)
    notion_id = sync.manifest.get_entry("docs/page.md")["notion_id"]
    result = sync.pull([notion_id, "docs/page.md"])

    # Option 3: Manual merge
    print("Local:", conflict["local_content"])
    print("Notion:", conflict["notion_content"])
    # Manually merge, then push with --force
```

### Create New Page

```python
sync = NotionSync()

# Create markdown file
with open("docs/new-page.md", "w") as f:
    f.write("""---
title: New Page
---

# New Page

This is my new page content.
""")

# Push to create in Notion
result = sync.push([
    "docs/new-page.md",
    "--parent-id", "parent-page-id-here"
])

print(f"Created: {result['notion_url']}")
```

### Check All Synced Files

```python
sync = NotionSync()

result = sync.status([])

for file in result["files"]:
    status = file["status"]
    path = file["path"]

    if status == "synced":
        print(f"✓ {path}")
    elif status == "local_modified":
        print(f"⚠ {path} (needs push)")
    elif status == "not_found":
        print(f"✗ {path} (missing)")
```

## Configuration

### Sync Directory

```python
# Default: ~/.notion-sync
sync = NotionSync()

# Custom location
sync = NotionSync("/path/to/sync-dir")
```

### API Token

```python
# From environment variable (recommended)
export NOTION_API_KEY="secret_xxx"
sync.pull(["abc123", "out.md"])

# Explicit token
sync.pull(["abc123", "out.md", "--notion-token", "secret_xxx"])
```

## File Structure

After pulling a page, you'll have:

```
docs/my-page.md           # Markdown file with frontmatter
~/.notion-sync/
├── manifest.json         # Sync state
└── blocks/
    └── abc123.json      # Raw blocks (if has rich content)
```

**my-page.md:**
```markdown
---
notion_id: abc123-def4-5678-90ab-cdef12345678
title: My Page
synced_at: 2026-03-28T10:30:00Z
---

# My Page

Content here...
```

## Tips

### Rich Blocks

Rich blocks (toggle, callout, table) are preserved:

```markdown
<details>
<summary>Click to expand</summary>
Hidden content here
</details>

<callout icon="💡" color="gray">
This is a callout block
</callout>
```

### Markdown Conversions

- Headings: `# H1`, `## H2`, `### H3`
- Lists: `- bullet`, `1. numbered`, `- [ ] todo`
- Code: ` ```python` ... ` ``` `
- Links: `[text](url)`
- Images: `![alt](url)`
- Bold: `**text**`
- Italic: `*text*`
- Code: `` `code` ``

### Avoiding Conflicts

1. **Pull before editing** if page might have changed
2. **Push frequently** to sync changes
3. **Use `--force`** carefully (overwrites Notion)
4. **Check status** regularly to catch drift

### Token Security

```bash
# Use environment variable (not in code)
export NOTION_API_KEY="secret_xxx"

# Or use .env file
echo "NOTION_API_KEY=secret_xxx" >> .env
source .env

# NEVER commit tokens to git
echo ".env" >> .gitignore
```

## Troubleshooting

### Error: "API key required"

```bash
# Set token
export NOTION_API_KEY="secret_xxx"

# Or pass explicitly
python3 lib/notion_sync.py pull abc123 out.md --notion-token secret_xxx
```

### Error: "Parent ID required"

When creating new pages, you must specify a parent:

```python
sync.push([
    "docs/new.md",
    "--parent-id", "parent-page-id"
])
```

### Error: "Page already synced"

The page is already synced to a different file:

```python
result = sync.pull(["abc123", "docs/duplicate.md"])
# Error: "Page already synced to: docs/original.md"

# Options:
# 1. Use the existing file
# 2. Remove from manifest first
sync.manifest.remove_entry("docs/original.md")
```

### Status shows "local_modified" but no changes

The file was modified without updating the manifest:

```python
# Force resync
sync.pull(["page-id", "docs/page.md"])
```

## Next Steps

- Read [Full API Documentation](./NOTION_SYNC_CLASS.md)
- See [Notion API Client](../lib/README.md#notion_apipy)
- Learn about [Per-Project State](./per-project-state.md)
- Run tests: `python3 test_notion_sync.py`

## Examples

See `examples/` directory for:
- `test_notion_api.py` - API client examples
- `project-setup/` - Real-world project structure
- More coming soon!

## Support

- File issues on GitHub
- Check existing documentation in `docs/`
- Run tests to verify installation
