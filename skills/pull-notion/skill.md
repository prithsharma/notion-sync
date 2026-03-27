---
name: pull-notion
description: Pull a Notion page to local markdown file for editing. Preserves rich blocks and tracks sync state.
disable-model-invocation: false
---

Pull a Notion page to a local markdown file for editing.

## Arguments

- **Page identifier** (required): Notion page URL or ID
- **Output path** (optional): Local file path. If omitted, creates file in current directory based on page title.

## What to do

1. **Parse arguments using LLM** (natural language understanding):
   - Extract Notion page identifier from user input:
     - URL format: `https://notion.so/workspace/Page-abc123` → extract `abc123`
     - URL with dashes: `https://notion.so/workspace/Page-Title-abc123def456` → extract `abc123def456`
     - UUID format: `abc123de-f456-7890-...` → normalize to raw ID (remove dashes)
     - Raw ID: `abc123def456` → use as-is
   - Determine output path:
     - If user provided a path, use it
     - Otherwise: will use current directory + page-title.md (CLI will determine exact name)
   - Get NOTION_API_KEY from environment or MCP config

2. **Call Python CLI** (fast execution via Bash tool):
   ```bash
   python3 ~/os/notion-sync/bin/notion-sync pull <page-id> <output-path> \
     --notion-token "$NOTION_API_KEY"
   ```

   The CLI outputs JSON with one of these structures:

   **Success:**
   ```json
   {
     "success": true,
     "operation": "pull",
     "file_path": "/absolute/path/to/file.md",
     "notion_id": "abc123def456",
     "title": "Page Title",
     "metadata": {
       "has_rich_blocks": true,
       "block_count": 42,
       "last_edited": "2026-03-28T10:30:00.000Z"
     }
   }
   ```

   **Error:**
   ```json
   {
     "error": "Error message",
     "type": "ErrorType",
     "status_code": 404
   }
   ```

3. **Parse JSON response using LLM** (error handling and decision making):

   **If error occurred:**

   - **AlreadySyncedError** with existing path:
     ```
     This page is already synced to {existing_path}.

     What would you like to do?
     1. Update that file instead
     2. Pull to new location (creates duplicate)
     3. Cancel
     ```
     Wait for user choice and act accordingly.

   - **NotionAPIError** with status 404:
     ```
     Page not found. Make sure:
     - The page ID is correct
     - The page is shared with the Notion integration
     - You have access to the workspace
     ```

   - **AuthenticationError**:
     ```
     Notion API token not found. Please set NOTION_API_KEY environment variable
     or configure the Notion MCP server.
     ```

   - **Other errors**:
     ```
     Failed to pull page: {error message}

     {Provide helpful suggestion based on error type}
     ```

   **If success:**
   - Extract metadata from response
   - Proceed to confirmation step

4. **Confirm to user using LLM** (natural language output):
   ```
   Successfully pulled "{title}" to {file_path}

   {if has_rich_blocks}
   Note: This page contains rich blocks (toggles, callouts, tables, etc.).
   They're preserved as special syntax and will sync back correctly.
   {endif}

   Next steps:
   - Edit the markdown file locally
   - When ready: /push-notion {file_path}
   - Check status: /notion-status {file_path}
   ```

## Important notes

- **Python CLI handles**: API calls, file I/O, hashing, manifest updates, conflict detection
- **LLM handles**: Natural language parsing, error explanation, user interaction, decision making
- **Performance**: ~1-2 seconds (vs 3-4 seconds with pure LLM/MCP approach)
- **Cost**: ~$0.01 per operation (vs ~$0.05 with MCP tools)
- **Notion token**: Retrieved from environment variable or MCP config
- **Working directory**: CLI accepts both absolute and relative paths

## Example usage

```bash
/pull-notion https://notion.so/workspace/Page-abc123
/pull-notion abc123def456 docs/api-reference.md
/pull-notion https://notion.so/My-Page-Title-abc123def456789 ~/projects/docs/page.md
```
