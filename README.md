# Notion Sync for Claude Code

> **Local-first Notion sync. Edit markdown locally, sync to Notion when ready.**

A bidirectional sync system that lets you edit Notion pages as markdown files in your favorite editor, then push changes back to Notion. Built as skills for [Claude Code](https://claude.ai/code).

## ✨ Features

- **🔄 Bidirectional sync** - Pull from Notion, edit locally, push back
- **⚡ Session-based** - Work offline, batch sync when ready
- **🎨 Rich block preservation** - Toggles, callouts, tables, columns stay intact
- **🔀 Conflict detection** - Warns when both local and Notion changed
- **👥 Team-friendly** - Share sync mappings via git
- **📦 Git-native** - Markdown files + manifest, all version controlled

## 🚀 Quick Start

### Prerequisites

- [Claude Code](https://claude.ai/code) installed
- Notion MCP server configured in Claude Code
- Access to your Notion workspace

### Installation

**Method 1: Plugin Installation (Recommended)**

```bash
# In Claude Code, use the plugin directory flag:
claude --plugin-dir /path/to/notion-sync

# Or for permanent installation, clone and symlink:
git clone https://github.com/prithsharma/notion-sync.git ~/.claude/plugins/notion-sync
```

Skills will be automatically available:
- `/pull-notion`
- `/push-notion`
- `/notion-status`

**Method 2: Via Setup Script**

```bash
git clone https://github.com/prithsharma/notion-sync.git
cd notion-sync
./scripts/setup-skills.sh
```

**Method 3: Submit to Plugin Marketplace** (Coming Soon)

```bash
# Once submitted to official marketplace:
/plugin install notion-sync
```

### First Sync

```bash
# In Claude Code:

# 1. Pull a Notion page
/pull-notion https://notion.so/your-page-url docs/my-doc.md

# 2. Edit the markdown file locally
# (uses your editor, or edit with Claude)

# 3. Push changes back
/push-notion docs/my-doc.md

# 4. Check sync status
/notion-status
```

## 📖 Usage

### Pull from Notion

```bash
# Pull to specific path
/pull-notion https://notion.so/page-url docs/architecture.md

# Pull to auto-generated path (uses page title)
/pull-notion https://notion.so/page-url

# Pull by page ID
/pull-notion abc123def456 docs/api.md
```

**What happens:**
- Creates local markdown file with frontmatter
- Preserves rich Notion blocks (toggles, callouts, tables)
- Updates `.notion-sync/manifest.json` with mapping
- Caches block data if needed

### Push to Notion

```bash
# Push existing synced file
/push-notion docs/architecture.md

# Force push (skip conflict detection)
/push-notion docs/architecture.md --force
```

**First-time push** (local file → new Notion page):
```bash
# Create markdown file
echo "# My Doc\nContent" > docs/new.md

# Optional: add frontmatter to specify parent
cat > docs/new.md << 'EOF'
---
notion_parent: "Team Docs"
---

# My Document
Content here...
EOF

# Push to Notion (notion_id added automatically)
/push-notion docs/new.md
```

**What happens:**
- Detects if both local and Notion changed (conflict detection)
- Shows diff if conflicts found
- Updates/creates Notion page
- Updates frontmatter with `notion_id`
- Updates manifest

### Check Status

```bash
# Show all synced files
/notion-status

# Check specific file
/notion-status docs/architecture.md

# Detailed view
/notion-status --verbose
```

**Output:**
```
Notion Sync Status
==================

✓ synced           docs/api-reference.md
✓ synced           docs/planning.md
⚠ local_modified   docs/architecture.md
✗ not_found        docs/old-doc.md

Summary: 2 synced, 1 modified, 1 not found
```

## 🏗️ How It Works

### Architecture

```
┌─────────────────────┐
│  Local Markdown     │
│  (your repo)        │
│                     │
│  docs/              │
│  ├── api.md         │◀─┐
│  └── arch.md        │  │
│                     │  │ Bidirectional
│  .notion-sync/      │  │ Sync
│  ├── manifest.json  │  │
│  └── blocks/        │  │
└─────────────────────┘  │
                         │
                         │
┌─────────────────────┐  │
│  Notion Workspace   │  │
│                     │  │
│  📄 API Docs        │◀─┘
│  📄 Architecture    │
│                     │
│  (Web/Desktop)      │
└─────────────────────┘
```

### Per-Project State

Each project using Notion sync has:

```
your-project/
├── docs/
│   └── *.md              # Markdown files with frontmatter
├── .notion-sync/
│   ├── manifest.json     # ✅ Commit (maps files to pages)
│   ├── config.json       # ✅ Commit (project defaults)
│   └── blocks/           # ❌ Don't commit (cache)
└── .gitignore            # Add: .notion-sync/blocks/
```

**Manifest** tracks which local files sync to which Notion pages:
```json
{
  "files": {
    "docs/api.md": {
      "notion_id": "abc123",
      "last_synced": "2026-03-28T10:30:00Z",
      "local_hash": "...",
      "notion_hash": "...",
      "notion_hash_at_sync": "..."
    }
  }
}
```

**Config** stores project defaults:
```json
{
  "default_parent": "Team Docs",
  "conflict_strategy": "ask"
}
```

### Frontmatter

Synced files have metadata in frontmatter:

```markdown
---
notion_id: abc123def456              # Notion page ID
notion_parent: "Team Documentation"  # Parent page
title: "API Reference"               # Page title
has_rich_blocks: false              # Rich content flag
last_synced: 2026-03-28T10:30:00Z   # Last sync time
---

# Your Content Here
```

### Conflict Detection

Three hashes track state for 3-way merge:

- `local_hash`: Current local content
- `notion_hash`: Current Notion content
- `notion_hash_at_sync`: Notion content at last sync (baseline)

**Scenarios:**

| Local changed? | Notion changed? | Result |
|---------------|-----------------|--------|
| ❌ | ❌ | ✓ Synced |
| ✅ | ❌ | ⚠ Local modified (safe to push) |
| ❌ | ✅ | ⚠ Notion modified (pull to update) |
| ✅ | ✅ | ⚡ **Conflict** (both changed) |

When conflict detected:
1. Show diff of both changes
2. Offer options: use local, use Notion, merge manually, cancel
3. For merge: edit local file to combine, re-push

## 🎨 Rich Blocks

Notion-flavored Markdown preserves rich formatting:

### Editable as-is:

**Toggles:**
```markdown
<details>
<summary>Click to expand</summary>
Content inside toggle
</details>
```

**Callouts:**
```markdown
<callout icon="💡">
This is a callout with an icon
</callout>
```

**Tables:**
```markdown
<table>
<tr>
  <td>Cell 1</td>
  <td>Cell 2</td>
</tr>
</table>
```

**Columns:**
```markdown
<columns>
  <column>Left column</column>
  <column>Right column</column>
</columns>
```

**Code blocks:**
````markdown
```javascript
const example = "preserved exactly";
```
````

### Complex blocks:

- Synced blocks - preserved
- Meeting notes with transcripts - transcript is read-only
- Embedded databases - preserved as references

**Tip:** For major edits to complex blocks, create a subpage in Notion and link it.

## 👥 Team Workflows

### Scenario 1: Developer edits locally

```bash
# 1. Pull latest
/pull-notion <url> docs/api.md

# 2. Edit locally
vim docs/api.md

# 3. Push changes
/push-notion docs/api.md

# 4. Commit both markdown and manifest
git add docs/api.md .notion-sync/manifest.json
git commit -m "Update API docs"
git push
```

### Scenario 2: PM edits on Notion

**PM:**
- Edits page directly on Notion

**Developer:**
```bash
# Pull latest before editing
/pull-notion <url> docs/api.md

# If you already edited locally, push will detect conflict:
/push-notion docs/api.md
# ⚡ Conflict detected!
# Choose: local, notion, merge, or cancel
```

### Scenario 3: New teammate joins

```bash
# Clone repo
git clone <repo-url>
cd <repo>

# Manifest shows what's synced
cat .notion-sync/manifest.json

# Pull latest from Notion
/pull-notion <url> docs/api.md

# Now in sync with team
```

## 📁 Project Setup

See [`examples/project-setup/`](./examples/project-setup/) for a complete example project structure.

**Quick setup for your project:**

```bash
# 1. Initialize sync directory
mkdir -p .notion-sync/blocks

# 2. Create manifest
cat > .notion-sync/manifest.json << 'EOF'
{
  "default_database": null,
  "files": {}
}
EOF

# 3. Create config (optional)
cat > .notion-sync/config.json << 'EOF'
{
  "default_parent": "Team Docs",
  "conflict_strategy": "ask"
}
EOF

# 4. Update .gitignore
echo ".notion-sync/blocks/" >> .gitignore

# 5. Pull your first page
/pull-notion <notion-url> docs/first-doc.md

# 6. Commit
git add .notion-sync/ docs/first-doc.md .gitignore
git commit -m "Setup Notion sync"
```

## 📚 Documentation

- **[Setup Guide](./docs/SETUP.md)** - Detailed installation and configuration
- **[Per-Project State](./docs/per-project-state.md)** - How the `.notion-sync/` directory works
- **[Conflict Resolution](./docs/conflict-resolution.md)** - Handling merge conflicts
- **[Rich Blocks Guide](./docs/rich-blocks.md)** - Working with Notion's advanced formatting
- **[Team Workflows](./docs/team-workflows.md)** - Collaboration patterns
- **[API Reference](./docs/api-reference.md)** - Skill parameters and options

## ⚙️ Configuration

### Per-project config

`.notion-sync/config.json`:
```json
{
  "default_parent": "Team Docs",
  "conflict_strategy": "ask"
}
```

Options:
- `default_parent`: Default Notion parent for new pages (null, page title, or URL)
- `conflict_strategy`: `ask`, `local`, `notion`, or `newer`

### Per-user overrides

`.notion-sync/config.local.json` (not committed):
```json
{
  "default_parent": "My Personal Docs",
  "conflict_strategy": "local"
}
```

## 🔧 Advanced Usage

### Custom parent for each file

In frontmatter:
```yaml
---
notion_parent: "Engineering/Backend"
---
```

Or use exact page URL:
```yaml
---
notion_parent: "https://notion.so/workspace/Backend-abc123"
---
```

### Bulk status check

```bash
/notion-status --verbose
```

Shows detailed status for all files.

### Force push (skip conflict detection)

```bash
/push-notion docs/api.md --force
```

Use with caution - overwrites Notion without checking.

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

**Development setup:**

```bash
# Fork and clone
git clone https://github.com/prithsharma/notion-sync.git
cd notion-sync

# Link skills for testing
./scripts/setup-skills.sh

# Make changes to skills/ or lib/

# Test with Claude Code
/pull-notion <test-url>
```

## 📝 License

MIT License - see [LICENSE](./LICENSE)

## 🙏 Acknowledgments

- Built for [Claude Code](https://claude.ai/code)
- Uses Notion's MCP server for API access
- Inspired by git's local-first philosophy

## 🐛 Issues & Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/notion-sync/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/notion-sync/discussions)

## 🗺️ Roadmap

- [ ] Bulk sync (`/sync-notion --all`)
- [ ] Watch mode (auto-push on file save)
- [ ] Interactive merge tool
- [ ] Template support
- [ ] Bidirectional link tracking
- [ ] CLI tool (use outside Claude Code)
- [ ] npm package distribution

---

**Made with ❤️ for local-first workflows**
