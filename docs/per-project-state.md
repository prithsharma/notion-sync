# Per-Project State

Understanding the `.notion-sync/` directory and how sync state is managed.

## Overview

Each project using Notion sync maintains state in a `.notion-sync/` directory (similar to `.git/`). This directory tracks:

- Which local files map to which Notion pages
- Content hashes for conflict detection
- Cached rich block data
- Project-specific configuration

## Directory Structure

```text
.notion-sync/
├── manifest.json          # ✅ Commit - file→page mappings
├── config.json            # ✅ Commit - project defaults
├── config.local.json      # ❌ Don't commit - user overrides
└── blocks/                # ❌ Don't commit - cache
    ├── abc123.json
    └── def456.json
```

## Manifest (`manifest.json`)

**Purpose:** Tracks which local files sync to which Notion pages.

**Commit this file:** ✅ Yes - so your team shares sync mappings.

**Structure:**

```json
{
  "default_database": null,
  "files": {
    "docs/architecture.md": {
      "notion_id": "abc123def456",
      "last_synced": "2026-03-28T10:30:00Z",
      "local_hash": "a1b2c3d4e5f6789...",
      "notion_hash": "a1b2c3d4e5f6789...",
      "notion_hash_at_sync": "a1b2c3d4e5f6789..."
    },
    "docs/api-reference.md": {
      "notion_id": "def456abc123",
      "last_synced": "2026-03-27T15:20:00Z",
      "local_hash": "f6e5d4c3b2a1098...",
      "notion_hash": "f6e5d4c3b2a1098...",
      "notion_hash_at_sync": "f6e5d4c3b2a1098..."
    }
  }
}
```

### Fields

**Root level:**

- `default_database`: Default Notion database ID (for database-backed pages, rarely used)
- `files`: Object mapping file paths to sync entries

**Per-file entry:**

- `notion_id`: The Notion page ID (UUID without dashes)
- `last_synced`: ISO 8601 timestamp of last successful sync
- `local_hash`: SHA-256 hash of current local content (excluding frontmatter)
- `notion_hash`: SHA-256 hash of current Notion content (from last fetch)
- `notion_hash_at_sync`: SHA-256 hash of Notion content at last sync (baseline for 3-way merge)

### Hash-based Conflict Detection

Three hashes enable 3-way merge conflict detection:

| Scenario | local_hash | notion_hash | notion_hash_at_sync | Status |
|----------|-----------|-------------|---------------------|--------|
| No changes | = manifest | = at_sync | = notion | ✓ Synced |
| Local edit only | ≠ manifest | = at_sync | = notion | ⚠ Local modified |
| Notion edit only | = manifest | ≠ at_sync | = at_sync | ⚠ Notion modified |
| Both edited | ≠ manifest | ≠ at_sync | ≠ both | ⚡ Conflict |

**Example workflow:**

```bash
# Initial state after pull:
{
  "local_hash": "aaa",
  "notion_hash": "aaa",
  "notion_hash_at_sync": "aaa"  # baseline
}

# You edit locally:
{
  "local_hash": "bbb",           # changed
  "notion_hash": "aaa",
  "notion_hash_at_sync": "aaa"
}
# Status: local_modified (safe to push)

# Meanwhile, someone edits on Notion:
{
  "local_hash": "bbb",
  "notion_hash": "ccc",          # changed (detected on push)
  "notion_hash_at_sync": "aaa"   # baseline shows both diverged
}
# Status: conflict (both changed since "aaa")
```

### Why Commit This?

**Team benefits:**

- Everyone knows which files sync to which Notion pages
- Consistent Notion organization across team
- PR reviews show "added sync for X doc"
- New teammates see what's synced

**Example PR:**

```diff
+ "docs/new-feature.md": {
+   "notion_id": "xyz789",
+   "last_synced": "2026-03-28T10:30:00Z",
+   ...
+ }
```

Reviewer sees: "We're now syncing new-feature.md to Notion page xyz789"

## Config (`config.json`)

**Purpose:** Project-wide defaults for sync behavior.

**Commit this file:** ✅ Yes - shared team configuration.

**Structure:**

```json
{
  "default_parent": "Team Documentation",
  "conflict_strategy": "ask"
}
```

### Fields

- **`default_parent`**: Where new pages are created in Notion
  - `null`: User's private pages (default)
  - `"Page Title"`: Find parent by title (searches workspace)
  - `"https://notion.so/workspace/Page-abc123"`: Exact page URL

- **`conflict_strategy`**: How to handle conflicts
  - `"ask"`: Prompt user each time (recommended)
  - `"local"`: Always prefer local version
  - `"notion"`: Always prefer Notion version
  - `"newer"`: Use most recently modified (by timestamp)

### Why Commit This?

Ensures consistent behavior across team. For example:

- All new docs go to "Team Documentation" parent
- Team agrees on conflict resolution strategy

## Local Config (`config.local.json`)

**Purpose:** Per-user overrides (not shared).

**Commit this file:** ❌ No - user-specific settings.

**Structure:**

```json
{
  "default_parent": "My Personal Docs",
  "conflict_strategy": "local"
}
```

Overrides `config.json` for your local environment.

**Use cases:**

- You want personal docs to go elsewhere
- You prefer different conflict strategy
- Testing/development overrides

**Create manually:**

```bash
cat > .notion-sync/config.local.json << 'EOF'
{
  "default_parent": "Personal/Work Notes",
  "conflict_strategy": "local"
}
EOF
```

## Blocks Cache (`blocks/`)

**Purpose:** Caches rich Notion block data for pages with complex formatting.

**Commit this directory:** ❌ No - derived data, can be regenerated.

**Structure:**

```text
blocks/
├── abc123def456.json
└── def456abc123.json
```

Each file stores the raw Notion API block data for a page.

**Example `blocks/abc123def456.json`:**

```json
{
  "page_id": "abc123def456",
  "blocks": [
    {
      "id": "blk_001",
      "type": "toggle",
      "toggle": {
        "rich_text": [{"type": "text", "text": {"content": "Toggle content"}}]
      },
      "children": [...]
    }
  ]
}
```

### When Created

Automatically created when pulling a page with rich blocks:

- Toggles (`<details>`)
- Callouts (`<callout>`)
- Complex tables
- Synced blocks
- Meeting notes

### Why Not Commit?

- **Large files**: Can be hundreds of KB for complex pages
- **Noisy diffs**: Changes on every pull, even if content unchanged
- **Regenerable**: Can be fetched from Notion anytime

### Regenerating

If blocks cache is missing or stale:

```bash
# Re-pull the page
/pull-notion <notion-url> docs/file.md
```

Blocks are automatically fetched and cached.

## Gitignore Recommendations

Add to your `.gitignore`:

```gitignore
# Notion sync cache (regenerated from Notion)
.notion-sync/blocks/

# User-specific config overrides
.notion-sync/config.local.json
```

**What to commit:**

```bash
.notion-sync/manifest.json    # ✅ Team file mappings
.notion-sync/config.json      # ✅ Project defaults
```

**What not to commit:**

```bash
.notion-sync/blocks/          # ❌ Cache
.notion-sync/config.local.json # ❌ User overrides
```

## State Lifecycle

### 1. First Pull

```bash
/pull-notion <url> docs/new-doc.md
```

**Actions:**

1. Creates `docs/new-doc.md` with frontmatter
2. Adds entry to `manifest.json`:

   ```json
   {
     "notion_id": "abc123",
     "last_synced": "2026-03-28T10:30:00Z",
     "local_hash": "xyz...",
     "notion_hash": "xyz...",
     "notion_hash_at_sync": "xyz..."
   }
   ```

3. If rich blocks: creates `blocks/abc123.json`

**All hashes match** = clean sync baseline.

### 2. Local Edit

```bash
vim docs/new-doc.md
# Make changes
```

**State change:**

- `local_hash`: ≠ manifest (changes computed on push)
- Other hashes: unchanged

**Status:** Local modified

### 3. Push

```bash
/push-notion docs/new-doc.md
```

**Actions:**

1. Compute new local_hash
2. Fetch current Notion content, compute notion_hash
3. Compare hashes:
   - If `notion_hash == notion_hash_at_sync`: No Notion changes, safe to push
   - If `notion_hash != notion_hash_at_sync`: Notion changed, conflict check
4. If conflict: show diff, ask user
5. If no conflict: push to Notion
6. Update manifest:

   ```json
   {
     "last_synced": "2026-03-28T11:45:00Z",
     "local_hash": "new...",
     "notion_hash": "new...",
     "notion_hash_at_sync": "new..."  // all now match
   }
   ```

### 4. Teammate Pull

Another developer:

```bash
git pull  # Gets updated manifest
/pull-notion <url> docs/new-doc.md
```

**Actions:**

1. Fetch from Notion
2. Update local file
3. Update manifest hashes

Now in sync with latest.

## File Moving

If you move a synced file:

```bash
git mv docs/old-path.md docs/new-path.md
```

**Manual manifest update:**

```json
{
  "files": {
    "docs/old-path.md": { ... }  // ❌ Remove
    "docs/new-path.md": { ... }  // ✅ Add (same notion_id)
  }
}
```

**Or re-pull:**

```bash
# Delete old entry
vim .notion-sync/manifest.json  # Remove old path

# Pull to new location
/pull-notion <url> docs/new-path.md
```

## Troubleshooting

### Manifest out of sync

**Symptom:** Hashes don't match reality, conflicts on every push.

**Fix:** Re-pull to reset state:

```bash
/pull-notion <url> docs/file.md --force
```

Or manually delete entry and re-pull:

```bash
# Edit manifest
vim .notion-sync/manifest.json
# Delete the entry for docs/file.md

# Re-pull
/pull-notion <url> docs/file.md
```

### Blocks cache missing

**Symptom:** Rich blocks not rendering correctly.

**Fix:** Re-pull:

```bash
/pull-notion <url> docs/file.md
```

### Config not applying

**Symptom:** Default parent not working.

**Check order of precedence:**

1. **Frontmatter** (highest priority)

   ```yaml
   ---
   notion_parent: "Specific Parent"
   ---
   ```

2. **Local config** `.notion-sync/config.local.json`

   ```json
   {"default_parent": "My Docs"}
   ```

3. **Project config** `.notion-sync/config.json`

   ```json
   {"default_parent": "Team Docs"}
   ```

4. **Default** (lowest priority): User's private pages

### Merge conflicts in manifest

**Symptom:** Git merge conflict in `manifest.json` after pull.

**Fix:**

```bash
# Both branches added entries - keep both
git checkout --ours .notion-sync/manifest.json
git checkout --theirs .notion-sync/manifest.json

# Manually merge (JSON is mergeable)
vim .notion-sync/manifest.json

# Or use jq to merge
jq -s '.[0] * .[1]' ours.json theirs.json > .notion-sync/manifest.json
```

Usually safe to keep both entries since they have different file paths or notion_ids.

## Best Practices

### 1. Commit manifest with docs

```bash
git add docs/api.md .notion-sync/manifest.json
git commit -m "Update API docs and sync state"
```

### 2. Don't edit manifest manually

Let the tools update it. Manual edits can break hash tracking.

**Exception:** Moving files or cleaning up old entries.

### 3. Review manifest in PRs

PRs that add docs should show manifest changes:

```diff
+ "docs/new-feature.md": {
+   "notion_id": "xyz789",
+   ...
+ }
```

Ensures team awareness of what's synced.

### 4. Regenerate blocks when needed

If blocks cache is huge or stale:

```bash
rm -rf .notion-sync/blocks/*
/pull-notion <url> docs/file.md  # Re-fetch
```

### 5. Use config.local for personal overrides

Don't change `config.json` for personal preferences. Use `config.local.json`:

```bash
cat > .notion-sync/config.local.json << 'EOF'
{
  "default_parent": "Personal",
  "conflict_strategy": "local"
}
EOF
```

Add to `.gitignore` so it's not committed.

## See Also

- [Setup Guide](./SETUP.md) - Initial configuration
- [Conflict Resolution](./conflict-resolution.md) - Handling conflicts
- [Team Workflows](./team-workflows.md) - Collaboration patterns
