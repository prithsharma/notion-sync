# Plugin Installation Guide

Notion Sync is distributed as a Claude Code plugin for easy installation and updates.

## Installation Methods

### Method 1: Local Plugin Directory (Quick Start)

Use the `--plugin-dir` flag to load the plugin:

```bash
# Clone the repository
git clone https://github.com/prithsharma/notion-sync.git
cd notion-sync

# Run Claude Code with the plugin
claude --plugin-dir .
```

Skills are immediately available:
- `/pull-notion`
- `/push-notion`
- `/notion-status`

### Method 2: Install to Plugins Directory (Permanent)

```bash
# Clone to Claude's plugins directory
git clone https://github.com/prithsharma/notion-sync.git ~/.claude/plugins/notion-sync

# Restart Claude Code or reload plugins
```

Skills will be available in all sessions.

### Method 3: Symlink (For Development)

If you're developing or want to track updates:

```bash
# Clone to your preferred location
git clone https://github.com/prithsharma/notion-sync.git ~/code/notion-sync

# Symlink to plugins directory
ln -s ~/code/notion-sync ~/.claude/plugins/notion-sync
```

Now you can `git pull` for updates.

### Method 4: Plugin Marketplace (Future)

Once submitted to the official Claude Code marketplace:

```bash
# In Claude Code:
/plugin install notion-sync
```

## Verification

After installation, verify the plugin is loaded:

```bash
# In Claude Code, check available skills:
/help

# You should see:
# - pull-notion: Pull Notion page to local markdown
# - push-notion: Push local markdown to Notion
# - notion-status: Show sync status
```

## Plugin Structure

The plugin includes:

```
notion-sync/
├── .claude-plugin/
│   ├── plugin.json          # Plugin manifest
│   └── marketplace.json     # Marketplace entry (for distribution)
├── skills/
│   ├── pull-notion/
│   ├── push-notion/
│   └── notion-status/
├── lib/                     # Core sync library
└── docs/                    # Documentation
```

## Configuration

The plugin requires the Notion MCP server. Ensure it's configured in your Claude Code settings:

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

See [SETUP.md](./SETUP.md) for detailed Notion MCP configuration.

## Updating the Plugin

### If using --plugin-dir or symlink:

```bash
cd /path/to/notion-sync
git pull
```

### If installed to plugins directory:

```bash
cd ~/.claude/plugins/notion-sync
git pull
```

### If using marketplace (future):

```bash
/plugin update notion-sync
```

## Uninstalling

### Remove from plugins directory:

```bash
rm -rf ~/.claude/plugins/notion-sync
```

### Or use the old setup script uninstall:

```bash
# Remove symlinked skills
rm ~/.claude/skills/pull-notion
rm ~/.claude/skills/push-notion
rm ~/.claude/skills/notion-status
```

## Troubleshooting

### "Plugin not found"

- Check the plugin is in `~/.claude/plugins/` or you're using `--plugin-dir`
- Verify `.claude-plugin/plugin.json` exists
- Restart Claude Code

### "Skills not appearing"

- Check plugin.json lists the correct skill paths
- Verify skill.md files exist in the skills/ directories
- Use `/help` to see all available skills

### "Notion MCP not available"

The plugin depends on the Notion MCP server. See [SETUP.md](./SETUP.md) for configuration instructions.

## Creating a Custom Marketplace

To distribute this plugin to your team via a custom marketplace:

1. **Fork or clone this repository**

2. **Host marketplace.json** (in `.claude-plugin/marketplace.json`)
   - Upload to GitHub, GitLab, or any accessible URL
   - Example: `https://raw.githubusercontent.com/your-org/marketplaces/main/marketplace.json`

3. **Configure Claude Code to use your marketplace:**

```json
{
  "pluginMarketplaces": [
    {
      "name": "Your Team Marketplace",
      "url": "https://your-url/marketplace.json"
    }
  ]
}
```

4. **Team members can now install:**

```bash
/plugin install notion-sync
```

## Submitting to Official Marketplace

To submit this plugin to the official Anthropic marketplace:

1. Visit https://platform.claude.com/plugins/submit
2. Submit the repository URL: `https://github.com/prithsharma/notion-sync`
3. Ensure all requirements are met:
   - ✅ Valid plugin.json manifest
   - ✅ MIT License
   - ✅ Comprehensive README
   - ✅ Clear documentation
   - ✅ Working skills

Once approved, users can install with:
```bash
/plugin install notion-sync
```

## See Also

- [Setup Guide](./SETUP.md) - Initial configuration
- [README](../README.md) - Overview and usage
- [Contributing](../CONTRIBUTING.md) - Development guide
