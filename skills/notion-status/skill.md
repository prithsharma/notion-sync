---
name: notion-status
description: Show sync status for all Notion-synced files. Displays which files are synced, modified, or have conflicts.
disable-model-invocation: false
---

Show sync status for all files tracked in the Notion sync manifest.

## Arguments

- **File path** (optional): Show status for specific file only
- **Verbose** (optional): `--verbose` or `-v` to show detailed information

## What to do

1. **Parse arguments:**
   - Check for file path (specific file) or none (all files)
   - Check for --verbose flag

2. **Call Python CLI (fast):**

   **For all files:**
   ```bash
   python3 ~/os/notion-sync/bin/notion-sync status
   ```

   **For specific file:**
   ```bash
   python3 ~/os/notion-sync/bin/notion-sync status <file-path>
   ```

   **For verbose:**
   ```bash
   python3 ~/os/notion-sync/bin/notion-sync status --verbose
   ```

3. **Parse JSON response:**

   The CLI returns JSON with this structure:
   ```json
   {
     "files": [
       {
         "path": "docs/api.md",
         "status": "synced",
         "notion_id": "abc123",
         "last_synced": "2026-03-28T10:30:00Z",
         "hashes": {
           "current": "...",
           "manifest": "...",
           "notion_at_sync": "..."
         }
       },
       {
         "path": "docs/guide.md",
         "status": "local_modified",
         "notion_id": "def456",
         "last_synced": "2026-03-27T15:00:00Z"
       }
     ]
   }
   ```

   Note: `hashes` field only present when --verbose is used.

4. **Format output for user:**

   **Compact view (default):**

   ```text
   Notion Sync Status
   ==================

   ✓ synced           docs/api.md
   ✓ synced           docs/planning.md
   ⚠ local_modified   docs/guide.md
   ✗ not_found        docs/old-doc.md

   Summary: 2 synced, 1 modified, 1 not found

   Next steps:
   - To push local changes: /push-notion docs/guide.md
   - To pull Notion updates: /pull-notion <url>
   ```

   **Verbose view:**

   ```text
   Notion Sync Status
   ==================

   File: docs/api.md
   Status: ✓ synced
   Notion ID: abc123def456
   Notion URL: https://notion.so/abc123def456
   Last synced: 2026-03-28T10:30:00Z
   Hashes:
     Current:  a1b2c3...
     Manifest: a1b2c3...
     Baseline: a1b2c3...
   ---

   File: docs/guide.md
   Status: ⚠ local_modified
   Notion ID: def456abc123
   Notion URL: https://notion.so/def456abc123
   Last synced: 2026-03-27T15:00:00Z
   Changes: Content modified locally since last sync
   Action: Run /push-notion docs/guide.md
   Hashes:
     Current:  d4e5f6... (changed)
     Manifest: a1b2c3...
     Baseline: a1b2c3...
   ---
   ```

5. **For single file status:**
   - Show detailed information even without --verbose
   - Include Notion page URL
   - Show suggested next action

6. **Summary statistics:**
   - Count files by status
   - Show total synced files
   - Highlight any conflicts or issues

## Status indicators

Use these in formatted output:
- `✓` - Synced (green concept - all hashes match)
- `⚠` - Modified locally (yellow concept - local changed)
- `⚡` - Conflict (red concept - both changed, rare in status check)
- `✗` - Not found (red concept - file deleted)
- `○` - Not synced (gray concept - in manifest but no file)

## Important notes

- Python CLI computes hashes and checks files (fast)
- LLM formats the output nicely (natural language)
- No Notion API calls (instant results)
- Speed: ~0.5 seconds (vs 2-3 seconds before)
- Cost: ~$0.005 (vs $0.02 before)
- Quick status check doesn't fetch from Notion (would be slow)
- To detect Notion-side changes, you'd need to run a full sync check
- Conflicts are only definitively detected during push operation
- Use this command before starting work to see what needs syncing

## Example usage

```bash
/notion-status
/notion-status docs/api-reference.md
/notion-status --verbose
```
