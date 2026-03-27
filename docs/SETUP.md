# Setup Guide

Detailed installation and configuration instructions for Notion Sync.

## Prerequisites

### 1. Claude Code

You need Claude Code installed. Available as:

- **CLI**: `npm install -g @anthropic/claude-code` or download from [claude.ai/code](https://claude.ai/code)
- **Desktop app**: Mac/Windows versions
- **IDE extensions**: VS Code, JetBrains

Check installation:

```bash
claude --version
```

### 2. Notion MCP Server

The Notion MCP server provides API access to your Notion workspace.

**Check if already configured:**

In Claude Code, run:

```bash
# If these tools are available, you're good to go:
# - mcp__notion__notion-fetch
# - mcp__notion__notion-create-pages
# - mcp__notion__notion-update-page
# - mcp__notion__notion-search
```

**If not configured**, see [Notion MCP Setup](#notion-mcp-setup) below.

### 3. Git (optional but recommended)

For version control and team collaboration:

```bash
git --version
```

## Installation

### Method 1: Clone & Setup (Recommended)

```bash
# 1. Clone this repository
git clone https://github.com/prithsharma/notion-sync.git
cd notion-sync

# 2. Run setup script
./scripts/setup-skills.sh

# 3. Verify installation
```

Open Claude Code and check:

```bash
/pull-notion
/push-notion
/notion-status
```

These commands should be available in the autocomplete.

### Method 2: Manual Installation

If the setup script doesn't work:

```bash
# 1. Clone repository
git clone https://github.com/prithsharma/notion-sync.git

# 2. Manually symlink skills
cd notion-sync
ln -s "$(pwd)/skills/pull-notion" ~/.claude/skills/pull-notion
ln -s "$(pwd)/skills/push-notion" ~/.claude/skills/push-notion
ln -s "$(pwd)/skills/notion-status" ~/.claude/skills/notion-status

# 3. Restart Claude Code
```

### Method 3: Copy Skills (No Git)

Download the repository as ZIP, extract, then:

```bash
# Copy skills to Claude Code directory
cp -r notion-sync/skills/* ~/.claude/skills/
```

## Notion MCP Setup

If you don't have the Notion MCP server configured:

### 1. Get Notion API Key

1. Go to [notion.so/my-integrations](https://notion.so/my-integrations)
2. Click "New integration"
3. Name it "Claude Code Sync"
4. Select the workspace
5. Copy the "Internal Integration Token"

### 2. Share Pages with Integration

For each page you want to sync:

1. Open the page in Notion
2. Click "..." menu → "Add connections"
3. Select your "Claude Code Sync" integration

Or share entire workspace:

1. Settings → Connections
2. Add your integration

### 3. Configure MCP Server

Add to your Claude Code MCP configuration:

**Location:** `~/.claude/mcp-config.json` or via Claude Code settings

```json
{
  "mcpServers": {
    "notion": {
      "command": "npx",
      "args": ["-y", "@notionhq/notion-mcp-server"],
      "env": {
        "NOTION_API_KEY": "your_notion_token_here"
      }
    }
  }
}
```

**Security note:** Don't commit this file with your token. Use environment variables:

```json
{
  "mcpServers": {
    "notion": {
      "command": "npx",
      "args": ["-y", "@notionhq/notion-mcp-server"],
      "env": {
        "NOTION_API_KEY": "${NOTION_API_KEY}"
      }
    }
  }
}
```

Then set in your shell:

```bash
export NOTION_API_KEY="your_token_here"
```

### 4. Restart Claude Code

After configuring MCP, restart Claude Code to load the server.

### 5. Verify

In Claude Code:

```text
Tell me about the Notion MCP tools you have access to.
```

Should list:

- `mcp__notion__notion-fetch`
- `mcp__notion__notion-create-pages`
- `mcp__notion__notion-update-page`
- `mcp__notion__notion-search`

## Project Setup

Set up Notion sync in your project:

### Quick Setup

```bash
# In your project directory
cd ~/your-project

# Create sync directory
mkdir -p .notion-sync/blocks

# Initialize manifest
cat > .notion-sync/manifest.json << 'EOF'
{
  "default_database": null,
  "files": {}
}
EOF

# Optional: create config
cat > .notion-sync/config.json << 'EOF'
{
  "default_parent": "Team Docs",
  "conflict_strategy": "ask"
}
EOF

# Update gitignore
cat >> .gitignore << 'EOF'

# Notion sync cache
.notion-sync/blocks/
.notion-sync/config.local.json
EOF

# Pull your first page (in Claude Code)
/pull-notion https://notion.so/your-page-url docs/first-doc.md

# Commit
git add .notion-sync/ docs/first-doc.md .gitignore
git commit -m "Setup Notion sync"
```

### Using the Example

Copy the example project structure:

```bash
cp -r notion-sync/examples/project-setup/.notion-sync ./
cp notion-sync/examples/project-setup/.gitignore ./

# Edit manifest to point to your files
vim .notion-sync/manifest.json
```

## Configuration

### Project-level Config

`.notion-sync/config.json` (committed, shared with team):

```json
{
  "default_parent": "Team Documentation",
  "conflict_strategy": "ask"
}
```

**Options:**

- **`default_parent`**: Where new pages go in Notion
  - `null`: User's private pages
  - `"Page Title"`: Find parent by title
  - `"https://notion.so/..."`: Exact page URL

- **`conflict_strategy`**: What to do when both sides changed
  - `"ask"`: Prompt user each time (recommended)
  - `"local"`: Always use local version
  - `"notion"`: Always use Notion version
  - `"newer"`: Use most recently modified

### User-level Config

`.notion-sync/config.local.json` (not committed, per-user):

```json
{
  "default_parent": "My Personal Docs",
  "conflict_strategy": "local"
}
```

Overrides project config for your local setup.

### Frontmatter Config

Per-file settings in markdown frontmatter:

```yaml
---
notion_parent: "Engineering/Backend/API"
title: "API Documentation"
---
```

Overrides both config files for this specific file.

## Verification

Test your setup:

### 1. Pull a page

```bash
/pull-notion https://notion.so/your-test-page
```

Should create a markdown file with frontmatter.

### 2. Edit locally

```bash
vim docs/test-page.md
# Make some changes
```

### 3. Check status

```bash
/notion-status docs/test-page.md
```

Should show "local_modified".

### 4. Push back

```bash
/push-notion docs/test-page.md
```

Should update Notion page.

### 5. Verify in Notion

Open the page in Notion web/desktop and confirm changes.

## Team Setup

### For the first team member (setting up)

```bash
# 1. Set up sync in your project
cd ~/team-project
# ... follow project setup above ...

# 2. Pull important pages
/pull-notion <url1> docs/architecture.md
/pull-notion <url2> docs/api-reference.md

# 3. Commit
git add .notion-sync/ docs/
git commit -m "Setup Notion sync for team docs"
git push
```

### For other team members (joining)

```bash
# 1. Clone repo (includes .notion-sync/)
git clone <repo-url>
cd team-project

# 2. Install Notion sync skills
cd ~/notion-sync
./scripts/setup-skills.sh

# 3. Configure Notion MCP (see above)

# 4. Pull latest from Notion
/pull-notion <url> docs/architecture.md
/pull-notion <url> docs/api-reference.md

# Now in sync!
```

**Note:** Team shares the manifest (file→page mappings) via git, but each person needs their own Notion MCP setup.

## Troubleshooting

### "Skill not found" error

Skills not installed correctly.

**Fix:**

```bash
cd ~/notion-sync
./scripts/setup-skills.sh
```

Restart Claude Code.

### "Notion MCP not available"

MCP server not configured.

**Fix:**

1. Check `~/.claude/mcp-config.json` has notion server
2. Verify NOTION_API_KEY is set
3. Restart Claude Code
4. In Claude Code, ask: "Do you have access to Notion MCP tools?"

### "Permission denied" on Notion page

Integration not shared with page.

**Fix:**

1. Open page in Notion
2. Click "..." → "Add connections"
3. Select your integration

### "Manifest not found"

Sync not initialized in project.

**Fix:**

```bash
mkdir -p .notion-sync/blocks
echo '{"default_database":null,"files":{}}' > .notion-sync/manifest.json
```

### Skills installed but not appearing

Claude Code may need cache refresh.

**Fix:**

```bash
# Remove old skills
rm -rf ~/.claude/skills/pull-notion
rm -rf ~/.claude/skills/push-notion
rm -rf ~/.claude/skills/notion-status

# Reinstall
cd ~/notion-sync
./scripts/setup-skills.sh

# Restart Claude Code
```

### "Page already synced to different path"

Trying to pull a page that's tracked elsewhere.

**Options:**

1. Update the existing file location
2. Create a new copy (unlink from manifest first)
3. Use the existing synced file

### Hashes don't match after pull

Content modified outside sync system.

**Fix:**

```bash
# Re-pull to reset
/pull-notion <url> docs/file.md --force
```

Or manually update hashes in manifest (advanced).

## Next Steps

- Read [Per-Project State](./per-project-state.md) to understand the sync directory
- See [Team Workflows](./team-workflows.md) for collaboration patterns
- Check [Rich Blocks Guide](./rich-blocks.md) for advanced formatting
- Review [examples/](../examples/) for project templates

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/prithsharma/notion-sync/issues)
- **Discussions**: [GitHub Discussions](https://github.com/prithsharma/notion-sync/discussions)
- **Claude Code docs**: [claude.ai/code/docs](https://claude.ai/code/docs)
- **Notion MCP docs**: [@notionhq/notion-mcp-server](https://github.com/notionhq/notion-mcp-server)
