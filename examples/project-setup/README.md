# Example Project Setup

This directory shows how to set up Notion sync in your own project.

## Structure

```text
your-project/
├── docs/
│   ├── architecture.md          # Synced with Notion
│   ├── api-reference.md         # Synced with Notion
│   └── local-only.md           # Not synced
├── .notion-sync/                # Per-project sync state
│   ├── manifest.json           # ✅ Commit this (team shares mappings)
│   ├── config.json             # ✅ Commit this (project defaults)
│   └── blocks/                 # ❌ Don't commit (cache, derived)
│       └── *.json
└── .gitignore                  # Add .notion-sync/blocks/
```

## Setup Steps

### 1. Initialize sync directory

```bash
mkdir -p .notion-sync/blocks
```

### 2. Create manifest.json

```json
{
  "default_database": null,
  "files": {}
}
```

This file tracks which local files sync to which Notion pages. It gets auto-updated by the sync tools, but you should commit it so your team knows what's synced.

### 3. Create config.json (optional)

```json
{
  "default_parent": "Team Docs",
  "conflict_strategy": "ask"
}
```

- `default_parent`: Default Notion parent page for new pages
- `conflict_strategy`: `ask`, `local`, `notion`, or `newer`

### 4. Update .gitignore

```gitignore
# Notion sync cache (derived data, don't commit)
.notion-sync/blocks/

# Optional: don't commit config overrides
.notion-sync/config.local.json
```

### 5. Pull your first page

```bash
/pull-notion https://notion.so/your-page-url docs/architecture.md
```

This will:

- Create `docs/architecture.md` with frontmatter
- Update `.notion-sync/manifest.json` with the mapping
- Cache rich blocks in `.notion-sync/blocks/` if needed

### 6. Commit the setup

```bash
git add .notion-sync/manifest.json .notion-sync/config.json docs/architecture.md
git commit -m "Add Notion sync for architecture doc"
```

## Team Collaboration

When a teammate pulls your repo:

1. They see which files sync to Notion (from manifest.json)
2. They can pull latest from Notion:

   ```bash
   /pull-notion <notion-url> docs/architecture.md
   ```

3. Or push their local changes:

   ```bash
   /push-notion docs/architecture.md
   ```

The manifest ensures everyone syncs to the same Notion pages.

## Example Frontmatter

After pulling/pushing, your markdown files will have frontmatter:

```markdown
---
notion_id: abc123def456
notion_parent: "Team Docs"
title: "Architecture Overview"
has_rich_blocks: false
last_synced: 2026-03-28T10:30:00Z
---

# Architecture Overview

Your content here...
```

This metadata:

- `notion_id`: Links to specific Notion page (auto-added)
- `notion_parent`: Where the page lives in Notion
- `title`: Page title (can override filename)
- `has_rich_blocks`: Whether page has toggles, callouts, etc.
- `last_synced`: When last synced (for reference)

## Workflows

### Solo: Local-first editing

```bash
# Pull latest
/pull-notion <url> docs/api.md

# Edit locally (fast, offline)
vim docs/api.md

# Push when ready
/push-notion docs/api.md
```

### Team: Collaborative editing

**Developer A** (working on Notion):

- Edits page on Notion web/desktop

**Developer B** (working locally):

```bash
# Before starting, pull latest
/pull-notion <url> docs/api.md

# Edit locally
vim docs/api.md

# Before pushing, check for conflicts
/notion-status docs/api.md

# Push (will detect if A also changed it)
/push-notion docs/api.md
```

If both changed:

- Tool shows diff
- Choose: use local, use Notion, or merge manually
- For merge: edit file to combine changes, re-push

## Tips

### What to sync?

**Good candidates:**

- API documentation
- Architecture docs
- Planning docs
- Team runbooks
- Meeting notes

**Poor candidates:**

- Auto-generated docs (just regenerate)
- Code comments (live in code)
- Frequently-changing content (use Notion directly)

### When to sync?

**Pull:**

- Start of work session
- Before making edits
- After team meetings (if notes updated)

**Push:**

- End of work session
- After major edits
- Before PR submission (so docs are live)

### Organizing in Notion

Use `notion_parent` in frontmatter to organize:

```markdown
---
notion_parent: "Engineering/Backend"
---
```

Or use URL for exact placement:

```markdown
---
notion_parent: "https://notion.so/workspace/Backend-abc123"
---
```

## Troubleshooting

### "File already synced to different path"

If you try to pull a page that's already synced elsewhere:

```bash
/pull-notion <url> new/path.md

# Error: Page abc123 already synced to docs/old-path.md
# Choose: update location, create copy, or cancel
```

### "Conflict detected"

Both local and Notion changed:

```bash
/push-notion docs/api.md

# Conflict detected!
# Local: +10 lines, -5 lines
# Notion: +3 lines, -2 lines
#
# Options:
# 1. local - Use local version
# 2. notion - Use Notion version
# 3. merge - Manual merge
# 4. cancel
```

For merge: edit `docs/api.md` to combine changes, then re-push.

### "Permission denied" on Notion

Make sure:

1. Notion MCP is configured in Claude Code
2. You have access to the page/workspace
3. Page isn't locked/archived

## Advanced: Config Overrides

Per-user settings (not committed):

```bash
# .notion-sync/config.local.json
{
  "default_parent": "My Personal Docs",
  "conflict_strategy": "local"
}
```

This overrides `config.json` for your local setup.
