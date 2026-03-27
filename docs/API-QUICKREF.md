# Notion API Quick Reference

Quick reference for `lib/notion_api.py` - copy-paste ready examples.

## Setup

```python
from lib.notion_api import NotionAPIClient

client = NotionAPIClient(api_key="secret_xxx")
```

## Fetch Page

```python
page = client.fetch_page("page-id-or-url")

# Access data
print(page['id'])              # abc-123-def
print(page['title'])           # Page Title
print(page['parent_title'])    # Parent or None
print(page['content'])         # Markdown content
print(len(page['blocks']))     # Number of blocks
```

## Create Page

```python
result = client.create_page(
    title="New Page",
    content="# Hello\n\nContent here.",
    parent_id="parent-page-id"
)

print(result['id'])    # New page ID
print(result['url'])   # Page URL
```

## Update Page

```python
client.update_page(
    page_id="page-id",
    content="# Updated\n\nNew content here."
)
```

## Search

```python
# Search all
results = client.search("documentation")

# Search pages only
results = client.search("API", filter_type="page")

# Access results
for item in results['results']:
    print(f"{item['type']}: {item['title']}")
    print(f"  ID: {item['id']}")
    print(f"  URL: {item['url']}")
```

## Error Handling

```python
from lib.notion_api import NotionAPIError, NotionRateLimitError

try:
    page = client.fetch_page("page-id")
except NotionRateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after}s")
except NotionAPIError as e:
    print(f"Error: {e}")
    print(f"Status: {e.status_code}")
```

## Markdown Examples

### Basic formatting

```python
content = """
# Main Heading

This is a paragraph with **bold** and *italic* text.

## Subheading

- Bulleted item
- Another item

1. Numbered item
2. Another item

> This is a quote

---

\`\`\`python
def hello():
    print("Hello, World!")
\`\`\`

- [ ] Todo item
- [x] Completed item
"""

client.create_page("Example", content, parent_id="...")
```

### Rich blocks

```python
content = """
# Rich Content

<details>
<summary>Click to expand</summary>
This is a toggle block.
</details>

<callout icon="💡" color="yellow">
This is a callout block.
</callout>

![Image description](https://example.com/image.png)

[Link to page](https://notion.so/...)
"""

client.update_page("page-id", content)
```

## ID Formats

All these work:

```python
# Raw ID (32 hex chars)
client.fetch_page("abc123def456abc123def456abc123de")

# UUID format
client.fetch_page("abc123de-f456-abc1-23de-f456abc123de")

# URL
client.fetch_page("https://notion.so/workspace/Page-Title-abc123def456")
```

## Command-Line

```bash
# Set API key
export NOTION_API_KEY="secret_xxx"

# Fetch page
python lib/notion_api.py $NOTION_API_KEY fetch <page-id>

# Search
python lib/notion_api.py $NOTION_API_KEY search "query"

# Create page
python lib/notion_api.py $NOTION_API_KEY create "Title" "# Content" <parent-id>

# Update page
python lib/notion_api.py $NOTION_API_KEY update <page-id> "# New content"
```

## Block Types

| Markdown | Notion Block |
|----------|--------------|
| `# Heading` | heading_1 |
| `## Heading` | heading_2 |
| `### Heading` | heading_3 |
| `Plain text` | paragraph |
| `- Item` | bulleted_list_item |
| `1. Item` | numbered_list_item |
| ` ```lang\ncode\n``` ` | code |
| `> Quote` | quote |
| `---` | divider |
| `- [ ] Task` | to_do (unchecked) |
| `- [x] Task` | to_do (checked) |
| `<details><summary>T</summary>C</details>` | toggle |
| `<callout icon="💡">Text</callout>` | callout |
| `![alt](url)` | image |
| `[text](url)` | bookmark |
| `[[Page Name]]` | child_page |

## Common Patterns

### Full page sync workflow

```python
# 1. Fetch from Notion
page = client.fetch_page("page-id")

# 2. Save to file
with open("doc.md", "w") as f:
    f.write(f"# {page['title']}\n\n")
    f.write(page['content'])

# 3. Edit locally
# ... user edits doc.md ...

# 4. Read updated content
with open("doc.md", "r") as f:
    content = f.read()

# 5. Push back to Notion
client.update_page(page['id'], content)
```

### Batch operations

```python
# Fetch multiple pages
page_ids = ["id1", "id2", "id3"]
pages = [client.fetch_page(pid) for pid in page_ids]

# Create multiple pages
parent_id = "parent-id"
titles = ["Page 1", "Page 2", "Page 3"]

for title in titles:
    result = client.create_page(
        title=title,
        content=f"# {title}\n\nContent for {title}",
        parent_id=parent_id
    )
    print(f"Created: {result['url']}")
```

### Search and process

```python
# Search for all pages with "API" in title
results = client.search("API", filter_type="page")

# Fetch and analyze each
for item in results['results']:
    page = client.fetch_page(item['id'])
    word_count = len(page['content'].split())
    print(f"{page['title']}: {word_count} words")
```

## Rate Limiting

```python
# Default: auto-retry on rate limits
client = NotionAPIClient(api_key, rate_limit_retry=True)

# Disable auto-retry
client = NotionAPIClient(api_key, rate_limit_retry=False)

# Manual rate limit handling
import time

try:
    page = client.fetch_page("page-id")
except NotionRateLimitError as e:
    time.sleep(e.retry_after)
    page = client.fetch_page("page-id")
```

## Debugging

```python
# Check what ID will be used
test_id = "https://notion.so/workspace/Page-abc123"
normalized = client._clean_id(test_id)
print(f"Will use ID: {normalized}")

# Check markdown conversion
blocks = client._markdown_to_blocks("# Test\n\nParagraph")
print(f"Generated {len(blocks)} blocks")
for block in blocks:
    print(f"  - {block['type']}")
```

## Integration with notion-sync

```python
# Use with sync-lib.js functions
import json
import subprocess

# Fetch page
page = client.fetch_page("page-id")

# Compute hash (compatible with sync-lib.js)
import hashlib
content_hash = hashlib.sha256(page['content'].encode()).hexdigest()

# Update manifest
manifest = {
    "files": {
        "docs/myfile.md": {
            "notion_id": page['id'],
            "local_hash": content_hash,
            "notion_hash": content_hash,
            "notion_hash_at_sync": content_hash
        }
    }
}
```

## See Also

- [Full API Documentation](./NOTION-API.md)
- [lib/README.md](../lib/README.md)
- [examples/test_notion_api.py](../examples/test_notion_api.py)

---

Copy-paste ready! For more details, see [NOTION-API.md](./NOTION-API.md).
