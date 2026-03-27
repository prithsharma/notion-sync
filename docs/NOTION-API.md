# Notion REST API Client

Documentation for the `notion_api.py` module.

## Overview

The Notion REST API client (`lib/notion_api.py`) provides a Python interface to Notion's REST API v1. It handles fetching, creating, and updating pages with automatic markdown conversion.

**Key Features:**
- Zero external dependencies (stdlib only)
- Automatic rate limit handling
- Recursive block fetching with pagination
- Bidirectional markdown conversion
- Rich block preservation
- Error handling with detailed exceptions

## Quick Start

```python
from lib.notion_api import NotionAPIClient

# Initialize
client = NotionAPIClient(api_key="secret_xxx")

# Fetch a page
page = client.fetch_page("page-id-or-url")
print(page['title'])
print(page['content'])

# Create a page
result = client.create_page(
    title="New Page",
    content="# Hello\n\nContent here.",
    parent_id="parent-page-id"
)

# Update a page
client.update_page(page_id, "# Updated\n\nNew content.")

# Search
results = client.search("query", filter_type="page")
```

## API Methods

### `NotionAPIClient(api_key, rate_limit_retry=True)`

Initialize the API client.

**Parameters:**
- `api_key` (str): Notion integration token (starts with `secret_`)
- `rate_limit_retry` (bool): Auto-retry on rate limits (default: True)

**Example:**
```python
client = NotionAPIClient("secret_abc123")
```

---

### `fetch_page(page_id) -> dict`

Fetch a page and convert to markdown.

**Parameters:**
- `page_id` (str): Page ID, UUID, or URL

**Returns:**
```python
{
    "id": "abc-123-def",           # Normalized UUID
    "title": "Page Title",          # Extracted from properties
    "content": "# Markdown...",     # Body content as markdown
    "parent_title": "Parent" or None,  # Parent page title
    "blocks": [...]                 # Raw block objects from API
}
```

**Example:**
```python
page = client.fetch_page("https://notion.so/workspace/Page-abc123")
print(f"Title: {page['title']}")
print(f"Parent: {page['parent_title']}")
print(f"\n{page['content']}")
```

---

### `create_page(title, content, parent_id) -> dict`

Create a new page.

**Parameters:**
- `title` (str): Page title
- `content` (str): Markdown content
- `parent_id` (str): Parent page ID (required)

**Returns:**
```python
{
    "id": "abc-123-def",            # New page ID
    "url": "https://notion.so/..."  # Page URL
}
```

**Example:**
```python
result = client.create_page(
    title="API Documentation",
    content="""
# Overview

This is the API documentation.

## Features

- Feature 1
- Feature 2

## Code Example

\`\`\`python
def example():
    return True
\`\`\`
    """,
    parent_id="parent-page-id-here"
)

print(f"Created: {result['url']}")
```

**Notes:**
- Maximum 100 blocks per create (API limitation)
- Parent page must be shared with your integration
- Parent is required (cannot create at workspace root via API)

---

### `update_page(page_id, content) -> dict`

Update page content.

**Parameters:**
- `page_id` (str): Page ID
- `content` (str): New markdown content

**Returns:**
```python
{
    "id": "abc-123-def",
    "success": True
}
```

**Example:**
```python
client.update_page(
    page_id="abc-123",
    content="""
# Updated Content

This replaces all existing content.

Note: Child pages are preserved.
    """
)
```

**Update Strategy:**
1. Fetch all existing blocks
2. Delete all blocks except child pages
3. Append new blocks from markdown
4. Handles batching automatically (100 blocks per request)

**Notes:**
- Child pages are preserved (not deleted)
- Other blocks are replaced
- Large updates are batched automatically

---

### `search(query, filter_type=None) -> dict`

Search the workspace.

**Parameters:**
- `query` (str): Search query
- `filter_type` (str, optional): Filter by "page" or "database"

**Returns:**
```python
{
    "results": [
        {
            "id": "abc-123",
            "title": "Page Title",
            "url": "https://notion.so/...",
            "type": "page"  # or "database"
        },
        ...
    ]
}
```

**Example:**
```python
# Search all
results = client.search("documentation")

# Search only pages
results = client.search("API", filter_type="page")

# Print results
for item in results['results']:
    print(f"[{item['type']}] {item['title']}")
    print(f"  {item['url']}")
```

---

## Block Conversion

The client automatically converts between Notion blocks and markdown.

### Supported Block Types

| Notion Block | Markdown | Notes |
|--------------|----------|-------|
| **paragraph** | Plain text | With rich text formatting |
| **heading_1** | `# Heading` | |
| **heading_2** | `## Heading` | |
| **heading_3** | `### Heading` | |
| **bulleted_list_item** | `- Item` | Supports nesting |
| **numbered_list_item** | `1. Item` | Supports nesting |
| **to_do** | `- [ ]` or `- [x]` | Checkbox items |
| **code** | ` ```lang\ncode\n``` ` | With language |
| **quote** | `> Quote` | |
| **divider** | `---` | |
| **toggle** | `<details><summary>Title</summary>Content</details>` | Preserved as HTML |
| **callout** | `<callout icon="💡" color="gray">Content</callout>` | Preserved as XML |
| **table** | `<table>...</table>` | Preserved as XML |
| **child_page** | `[[Page Name]]` | Wiki-style link |
| **link_to_page** | `[Link](page_id)` | |
| **image** | `![alt](url)` | |
| **video** | `[video](url)` | |
| **file** | `[file](url)` | |
| **bookmark** | `[title](url)` | |

### Rich Text Formatting

Notion rich text formatting is converted to markdown:

| Notion | Markdown |
|--------|----------|
| Bold | `**text**` |
| Italic | `*text*` |
| Strikethrough | `~~text~~` |
| Code | `` `text` `` |
| Link | `[text](url)` |

### Rich Block Preservation

Complex Notion blocks are preserved as XML-like syntax:

**Toggle blocks:**
```markdown
<details>
<summary>Click to expand</summary>
Content here...
</details>
```

**Callout blocks:**
```markdown
<callout icon="💡" color="gray">
Important information here.
</callout>
```

**Table blocks:**
```markdown
<table width="3">
| Column 1 | Column 2 | Column 3 |
| Cell 1 | Cell 2 | Cell 3 |
</table>
```

This allows round-trip editing without losing structure.

---

## Error Handling

### Exception Hierarchy

```
Exception
└── NotionAPIError
    └── NotionRateLimitError
```

### `NotionAPIError`

Base exception for all API errors.

**Attributes:**
- `message` (str): Error message
- `status_code` (int): HTTP status code
- `response` (dict): API response body

**Example:**
```python
from lib.notion_api import NotionAPIError

try:
    page = client.fetch_page("invalid-id")
except NotionAPIError as e:
    print(f"Error: {e}")
    print(f"Status: {e.status_code}")
    if e.response:
        print(f"Details: {e.response}")
```

### `NotionRateLimitError`

Raised when rate limit is exceeded (HTTP 429).

**Attributes:**
- `retry_after` (int): Seconds to wait before retrying

**Example:**
```python
from lib.notion_api import NotionRateLimitError

try:
    page = client.fetch_page("page-id")
except NotionRateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds.")
    time.sleep(e.retry_after)
    page = client.fetch_page("page-id")  # Retry
```

**Note:** Rate limits are automatically handled if `rate_limit_retry=True` (default).

---

## Rate Limiting

Notion API has rate limits:
- 3 requests per second per integration
- Bursts allowed, but sustained high rate triggers 429

The client handles this automatically:

1. **Automatic retry:** Retries on 429 with exponential backoff
2. **Respects `Retry-After` header:** Waits as long as Notion requests
3. **Configurable:** Set `rate_limit_retry=False` to disable

**Example:**
```python
# Auto-retry enabled (default)
client = NotionAPIClient(api_key, rate_limit_retry=True)

# Auto-retry disabled
client = NotionAPIClient(api_key, rate_limit_retry=False)
```

---

## Advanced Usage

### ID Normalization

The client accepts multiple ID formats:

```python
# All of these work:
page = client.fetch_page("abc123def456abc123def456abc123de")  # Raw
page = client.fetch_page("abc123de-f456-abc1-23de-f456abc123de")  # UUID
page = client.fetch_page("https://notion.so/workspace/Page-Title-abc123def456abc123def456abc123de")  # URL
```

IDs are normalized to UUID format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

### Parent Title Resolution

`fetch_page()` attempts to fetch the parent page title:

```python
page = client.fetch_page("page-id")
if page['parent_title']:
    print(f"Parent: {page['parent_title']}")
else:
    print("At workspace root or database")
```

### Batch Updates

`update_page()` automatically batches large updates:

```python
# Create 500 paragraphs of content
content = "\n\n".join([f"Paragraph {i}" for i in range(500)])

# Automatically batched into 5 requests (100 blocks each)
client.update_page("page-id", content)
```

### Custom Block Conversion

To handle custom block types, extend the client:

```python
class CustomNotionClient(NotionAPIClient):
    def _blocks_to_markdown(self, blocks, level=0):
        # Add custom logic here
        return super()._blocks_to_markdown(blocks, level)

    def _markdown_to_blocks(self, markdown):
        # Add custom logic here
        return super()._markdown_to_blocks(markdown)
```

---

## Command-Line Interface

The module includes a CLI for testing:

```bash
python lib/notion_api.py <api_key> <command> [args...]
```

**Commands:**

```bash
# Fetch a page
python lib/notion_api.py $API_KEY fetch <page-id>

# Search
python lib/notion_api.py $API_KEY search "query"

# Create a page
python lib/notion_api.py $API_KEY create "Title" "Content" <parent-id>

# Update a page
python lib/notion_api.py $API_KEY update <page-id> "New content"
```

**Example:**
```bash
export NOTION_API_KEY="secret_xxx"

# Fetch and display a page
python lib/notion_api.py $NOTION_API_KEY fetch abc123def456

# Search for documentation
python lib/notion_api.py $NOTION_API_KEY search "documentation"
```

---

## Testing

See `examples/test_notion_api.py` for interactive examples.

**Setup:**
1. Create a Notion integration: https://www.notion.so/my-integrations
2. Copy your integration token (starts with `secret_`)
3. Share pages with your integration

**Run examples:**
```bash
export NOTION_API_KEY="secret_xxx"
python examples/test_notion_api.py
```

**Basic test:**
```python
import sys
sys.path.insert(0, 'lib')
from notion_api import NotionAPIClient

client = NotionAPIClient("secret_xxx")

# Test search
results = client.search("test")
print(f"Found {len(results['results'])} results")

# Test fetch (replace with your page ID)
page = client.fetch_page("your-page-id")
print(f"Title: {page['title']}")
print(f"Content length: {len(page['content'])} chars")
```

---

## Implementation Notes

### Design Decisions

**Why stdlib only?**
- Simplifies deployment
- No dependency conflicts
- Works everywhere Python 3.7+ runs

**Why preserve rich blocks as XML?**
- Round-trip fidelity
- Editable in text editor
- Future-proof (can parse later)

**Why delete-then-append for updates?**
- Notion API doesn't support atomic replace
- Preserves child pages (important!)
- Handles any content changes

### Limitations

**API Limitations:**
- Cannot create pages at workspace root (need parent)
- 100 blocks per create/append request
- Rate limits (3 req/sec sustained)
- Temporary URLs for media (expire after 1 hour)

**Block Coverage:**
- Most common blocks supported
- Some specialized blocks (embed, equation) preserved as comments
- Databases not fully supported (use MCP for complex DB operations)

**Markdown Conversion:**
- Basic formatting works well
- Complex nested structures may need manual editing
- Tables preserved as XML (complex to convert)

### Future Enhancements

Possible improvements:
- [ ] Two-column layout support
- [ ] Synced blocks parsing
- [ ] Database property editing
- [ ] Media file upload
- [ ] Better table markdown conversion
- [ ] Equation block support
- [ ] Embed block handling

---

## Troubleshooting

### Common Issues

**"Invalid Notion page ID"**
- Check ID format (32 hex chars)
- Try using the full URL
- Verify page exists

**"object not found"**
- Page not shared with integration
- Go to page → Share → Select your integration

**"unauthorized"**
- Invalid API key
- Key revoked or expired
- Check token in integration settings

**"Rate limit exceeded"**
- Too many requests
- Enable `rate_limit_retry=True` (default)
- Add delays between requests

**"validation_error" on create**
- Parent ID invalid or not accessible
- Content exceeds API limits
- Check parent page permissions

### Debug Mode

Add debug output:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

client = NotionAPIClient(api_key)
# Now see all HTTP requests
```

---

## See Also

- [Notion API Documentation](https://developers.notion.com/)
- [lib/sync-lib.js](../lib/sync-lib.js) - JavaScript sync utilities
- [examples/test_notion_api.py](../examples/test_notion_api.py) - Usage examples
- [docs/per-project-state.md](./per-project-state.md) - Sync state management

---

**Built for notion-sync** - Local-first Notion editing for Claude Code
