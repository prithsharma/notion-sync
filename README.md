# Notion Sync for Claude Code

> **Local-first Notion sync. Edit markdown locally, sync to Notion when ready.**

A bidirectional sync system for [Claude Code](https://claude.ai/code) that lets you edit Notion pages as markdown files, then push changes back.

[![GitHub](https://img.shields.io/github/stars/prithsharma/notion-sync?style=social)](https://github.com/prithsharma/notion-sync)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- 🔄 **Bidirectional sync** - Pull from Notion, edit locally, push back
- ⚡ **Session-based** - Work offline, batch sync when ready
- 🎨 **Rich blocks** - Toggles, callouts, tables, columns preserved
- 🔀 **Conflict detection** - Warns when both sides changed
- 👥 **Team-friendly** - Share sync mappings via git
- 📦 **Git-native** - Markdown files + manifest, all version controlled

## 🚀 Quick Start

### Prerequisites

- [Claude Code](https://claude.ai/code) installed
- [Notion MCP server](https://github.com/notionhq/notion-mcp-server) configured
- Access to your Notion workspace

### Installation

**Method 1: Plugin (Recommended)**

```bash
# Clone and use as plugin
git clone https://github.com/prithsharma/notion-sync.git
claude --plugin-dir ./notion-sync
```

**Method 2: Install Permanently**

```bash
git clone https://github.com/prithsharma/notion-sync.git ~/.claude/plugins/notion-sync
# Restart Claude Code
```

See [Plugin Installation Guide](./docs/PLUGIN-INSTALLATION.md) for all methods.

### First Sync

```bash
# In Claude Code:

# 1. Pull a Notion page
/pull-notion https://notion.so/your-page-url docs/my-doc.md

# 2. Edit the markdown file locally
vim docs/my-doc.md

# 3. Push changes back to Notion
/push-notion docs/my-doc.md

# 4. Check sync status
/notion-status
```

## 📖 Usage

### Available Skills

- **`/pull-notion <url> [path]`** - Pull Notion page to local markdown
- **`/push-notion <file>`** - Push local markdown to Notion
- **`/notion-status [file]`** - Show sync status

### Basic Workflow

```bash
# Start of session: Pull latest
/pull-notion <url> docs/architecture.md

# Edit locally (fast, offline)
# ... make changes ...

# End of session: Push changes
/push-notion docs/architecture.md
```

### Create New Page in Notion

```bash
# Create local file
cat > docs/new-feature.md << 'EOF'
---
notion_parent: "Team Docs"
---

# New Feature
Content here...
EOF

# Push to Notion (creates page under "Team Docs")
/push-notion docs/new-feature.md
```

### Team Collaboration

**Setup per-project sync:**

```bash
cd ~/your-project

# Initialize sync directory
mkdir -p .notion-sync/blocks
echo '{"default_database":null,"files":{}}' > .notion-sync/manifest.json

# Add to gitignore
echo ".notion-sync/blocks/" >> .gitignore

# Pull first document
/pull-notion <url> docs/first-doc.md

# Commit manifest (team shares mappings)
git add .notion-sync/manifest.json docs/first-doc.md .gitignore
git commit -m "Setup Notion sync"
```

**Teammates:** Just run `/pull-notion <url> docs/first-doc.md` to sync.

## 🏗️ How It Works

Notion Sync uses a local `.notion-sync/` directory per-project:

```text
your-project/
├── docs/
│   └── *.md              # Markdown with frontmatter
├── .notion-sync/
│   ├── manifest.json     # ✅ Commit (file→page mappings)
│   ├── config.json       # ✅ Commit (project defaults)
│   └── blocks/           # ❌ Don't commit (cache)
└── .gitignore
```

**Manifest** tracks which files sync to which Notion pages with SHA-256 hashes for 3-way conflict detection.

**Frontmatter** in markdown files:

```yaml
---
notion_id: abc123def456              # Notion page ID
notion_parent: "Team Documentation"  # Parent page
title: "API Reference"               # Page title
has_rich_blocks: false               # Rich content flag
last_synced: 2026-03-28T10:30:00Z    # Last sync
---
```

## 🔀 Conflict Detection

When both local and Notion changed:

```text
⚡ Conflict detected!

Local changes:  + New section added
Notion changes: + Diagram added by teammate

Options:
  1. local  - Use your local version
  2. notion - Use Notion version
  3. merge  - Manual merge (edit file, re-push)
  4. cancel - Abort
```

## 📁 Project Setup

See [`examples/project-setup/`](./examples/project-setup/) for a complete template.

**Quick setup:**

```bash
mkdir -p .notion-sync/blocks
echo '{"default_database":null,"files":{}}' > .notion-sync/manifest.json
echo ".notion-sync/blocks/" >> .gitignore
```

**Config (optional):**

```json
{
  "default_parent": "Team Docs",
  "conflict_strategy": "ask"
}
```

## 📚 Documentation

- **[Plugin Installation](./docs/PLUGIN-INSTALLATION.md)** - Installation methods, plugin system, marketplace
- **[Setup Guide](./docs/SETUP.md)** - Initial configuration, Notion MCP setup
- **[Per-Project State](./docs/per-project-state.md)** - Understanding `.notion-sync/`, manifest, hashes
- **[Contributing](./CONTRIBUTING.md)** - Development guide

## ⚙️ Configuration

**Per-project** (`.notion-sync/config.json`):

```json
{
  "default_parent": "Team Docs",
  "conflict_strategy": "ask"
}
```

**Per-user** (`.notion-sync/config.local.json`, not committed):

```json
{
  "default_parent": "My Personal Docs",
  "conflict_strategy": "local"
}
```

**Per-file** (frontmatter):

```yaml
---
notion_parent: "Engineering/Backend"
---
```

## 🎨 Rich Blocks

Notion-flavored Markdown preserves formatting:

- **Toggles**: `<details><summary>Text</summary>Content</details>`
- **Callouts**: `<callout icon="💡">Text</callout>`
- **Tables**: `<table>...</table>`
- **Columns**: `<columns><column>...</column></columns>`
- **Code blocks**: ` ```language\ncode\n``` `

Most rich blocks are editable as-is. For complex edits, create a subpage in Notion.

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](./CONTRIBUTING.md).

**Development:**

```bash
git clone https://github.com/prithsharma/notion-sync.git
cd notion-sync
claude --plugin-dir .
# Test skills with /pull-notion, /push-notion, /notion-status
```

## 🐛 Issues & Support

- **Issues**: [GitHub Issues](https://github.com/prithsharma/notion-sync/issues)
- **Discussions**: [GitHub Discussions](https://github.com/prithsharma/notion-sync/discussions)

## 📝 License

MIT License - see [LICENSE](./LICENSE)

## 🙏 Acknowledgments

- Built for [Claude Code](https://claude.ai/code)
- Uses [Notion MCP](https://github.com/notionhq/notion-mcp-server) for API access
- Inspired by git's local-first philosophy

---

**Made with ❤️ for local-first workflows**
