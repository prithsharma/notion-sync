---
name: push-notion
description: Push local markdown file to Notion. Creates new page or updates existing. Detects conflicts and performs section-based updates.
disable-model-invocation: false
---

Push a local markdown file to Notion, creating or updating the page.

## Arguments

- **File path** (required): Path to local markdown file to push
- **Force** (optional): `--force` to skip conflict detection and force push

## What to do

1. **Parse arguments:**
   - Extract file path from user input (convert to absolute path if relative)
   - Check for `--force` flag in arguments
   - Extract `NOTION_API_KEY` from environment variables

2. **Call Python CLI:**
   Run the notion-sync push command via Bash:

   ```bash
   python3 ~/os/notion-sync/bin/notion-sync push <absolute-file-path> \
     ${force_flag} --notion-token "$NOTION_API_KEY"
   ```

   The CLI will output JSON response to stdout.

3. **Handle response based on status:**

   **Case A: Conflict detected**
   ```json
   {
     "success": false,
     "conflict": {
       "local_changed": true,
       "notion_changed": true,
       "local_content": "...",
       "notion_content": "..."
     },
     "file_path": "docs/file.md",
     "notion_id": "abc123"
   }
   ```

   LLM action:
   - Show diff between local and Notion versions (both changed)
   - Ask user: "Both local and Notion have changes. What do you want to do?
     1. **local** - Use your local version (overwrite Notion)
     2. **notion** - Use Notion's version (discard local changes)
     3. **merge** - I'll show you both versions so you can manually merge
     4. **cancel** - Abort this push"

   Based on user choice:
   - **"local"** -> Re-run: `notion-sync push <file> --force`
   - **"notion"** -> Call: `notion-sync fetch <page-id>`, which will update local file and manifest
   - **"merge"** -> Show both contents side-by-side in a clear format, instruct user to edit the file to resolve conflicts, then re-run push
   - **"cancel"** -> Exit gracefully with no changes

   **Case B: Parent not found** (when creating new page)
   ```json
   {
     "success": false,
     "error": "parent_not_found",
     "parent_name": "Team Docs"
   }
   ```

   LLM action:
   - Use `mcp__notion__notion-search` to find pages matching the parent name
   - If multiple matches, show options to user with titles and paths
   - User picks one -> Re-run push with updated frontmatter or `--parent-id <id>` flag

   **Case C: Success**
   ```json
   {
     "success": true,
     "operation": "create" | "update",
     "notion_id": "abc123",
     "file_path": "docs/file.md",
     "notion_url": "https://notion.so/abc123"
   }
   ```

   LLM action:
   - Show success message:
     ```
     Successfully {operation === "create" ? "created" : "updated"} page in Notion

     File: {file_path}
     Notion URL: {notion_url}

     The local file and Notion page are now in sync.
     ```

   **Case D: Error**
   ```json
   {
     "success": false,
     "error": "error_type",
     "message": "Error description"
   }
   ```

   LLM action:
   - Parse error type and show helpful message
   - Suggest recovery actions based on error type

4. **Parent resolution helper:**
   When creating a new page without parent ID in frontmatter:
   - If frontmatter has `notion_parent: "Some Page Name"` but no ID
   - Use `mcp__notion__notion-search` with query: "Some Page Name" and type: "page"
   - Show results to user with context (parent page paths if available)
   - User picks one -> Get page ID and re-run push
   - This is where LLM's natural language understanding and disambiguation shines

## Important notes

- **Speed**: ~1-2 seconds for normal operations (vs 3-5 seconds with pure LLM approach)
- **Cost**: ~$0.01-0.02 for normal operations, ~$0.05 for conflicts (vs $0.05-0.10 before)
- **Division of labor**:
  - Python CLI handles: Reading file, conflict detection, API push, manifest update
  - LLM handles: Conflict resolution decisions, parent search/disambiguation, error explanation
- **Interactive conflict resolution**: This is where the LLM excels - understanding user intent and showing diffs clearly
- **Conflict detection**: The Python CLI compares hashes to detect conflicts before attempting push
- **Manifest updates**: Python CLI updates `~/.notion-sync/manifest.json` automatically on successful push

## Example usage

```bash
/push-notion docs/api-reference.md
/push-notion docs/api-reference.md --force
```
