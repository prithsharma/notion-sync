# Notion Markdown Sync Tools - Research Summary

Research Date: 2026-03-27

## Executive Summary

The Notion markdown sync space has **three distinct categories**:

1. **Conversion Libraries** - Focus on converting Notion blocks to markdown (e.g., notion-to-md with 1,676 stars)
2. **Backup Tools** - One-way sync from Notion to local files (e.g., notion-export-client with 156 stars)
3. **Bidirectional Sync Tools** - True sync with local-first editing (emerging category, smaller projects)

**Key Finding**: There is **no dominant established solution** for local-first bidirectional Notion sync. Most tools are either:
- One-way export/backup tools
- Obsidian-focused migration tools
- GitHub Actions for specific workflows

The **Claude Code plugin space** is nascent but growing, with the official Notion plugin (281 stars) being the main integration.

---

## Category 1: Claude Code Plugins

### 1. claude-code-notion-plugin (Official)
- **URL**: https://github.com/makenotion/claude-code-notion-plugin
- **Stars**: 281
- **Updated**: 2026-03-27
- **Type**: Claude Code Plugin
- **Tech Stack**: Plugin + Notion MCP Server

**Features**:
- Official Notion plugin for Claude Code
- Bundles Notion Skills from cookbook
- Integrated Notion MCP Server
- Slash commands for common workflows
- OAuth authentication

**Capabilities**:
- Search workspace
- Create/update pages
- Query databases
- Knowledge capture
- Meeting intelligence
- Research documentation
- Spec to implementation

**Unique Aspects**:
- Official support from Notion
- MCP server integration
- Not a sync tool - provides direct API access within Claude Code
- Focus on AI-assisted workflows rather than local markdown editing

**Installation**: Via Claude Code plugin marketplace

---

### 2. nsync - Notion Sync Tool
- **URL**: https://github.com/miyatti777/nsync
- **Stars**: 1 (very new)
- **Updated**: 2026-03-27
- **Language**: Python
- **Type**: CLI + Claude Skill

**Features**:
- **Bidirectional sync** with conflict detection
- Local-first markdown editing
- Media file support (images, PDFs, videos, audio)
- Database to SQLite conversion
- Zero external dependencies (stdlib only)
- Claude Skill compatible
- Position-aware child page links
- Automatic file upload to Notion

**Sync Direction**: Bidirectional
- Pull: Notion → Local markdown
- Push: Local markdown → Notion
- Conflict detection with manual resolution

**Tech Stack**: Pure Python 3.7+ (no dependencies except optional PyYAML)

**Workflow**:
```bash
nsync.py init <notion-url> [dir]  # Initialize workspace
nsync.py sync                      # Bidirectional sync
nsync.py pull <file>               # Pull specific page
nsync.py push <file>               # Push specific page
nsync.py query <db> "SQL"          # Query SQLite DBs
```

**Unique Features**:
- Front matter with notion_id tracking
- Workspace structure with sync state
- Incremental sync with content hashing
- Rate limit handling with checkpoints
- Multi-data source DB support
- Automatic rename detection
- Child page scaffold generation

**Limitations**:
- Very new project (1 star)
- Japanese documentation (with some English)
- Not widely tested

---

## Category 2: Conversion Libraries

### 3. notion-to-md (Most Popular)
- **URL**: https://github.com/souvikinator/notion-to-md
- **Stars**: 1,676 ⭐⭐⭐
- **Updated**: 2026-03-27
- **Language**: TypeScript/JavaScript
- **Type**: npm package / conversion library

**Features**:
- Convert Notion to multiple formats: Markdown, MDX, JSX, HTML, LaTeX
- Works with Notion API
- Building block for static site generators
- Well-documented API
- Active maintenance

**Sync Direction**: One-way (Notion → Markdown)

**Use Cases**:
- Static site generation
- Documentation pipelines
- CMS integration
- Not designed for local editing + sync back

**npm Package**: `notion-to-md` (v3.1.9)

**Unique Aspects**:
- Most mature conversion library
- Format flexibility
- Strong community adoption
- Focus on publishing workflows, not editing

---

### 4. @notionhq/notion-mcp-server
- **URL**: Official Notion MCP Server
- **Type**: MCP (Model Context Protocol) Server
- **npm**: `@notionhq/notion-mcp-server`

**Features**:
- Official Notion MCP implementation
- Search, retrieve, create, update capabilities
- OAuth support
- Used by claude-code-notion-plugin

**Not a sync tool** - provides API access layer for AI tools

---

## Category 3: Bidirectional Sync Tools

### 5. notionfs
- **URL**: https://github.com/can1357/notionfs
- **Stars**: 12
- **Updated**: 2026-03-26
- **Language**: Python
- **Type**: CLI tool

**Features**:
- **Bidirectional sync** with conflict detection
- Markdown native editing
- YAML frontmatter for properties
- Watch mode for continuous sync
- Offline-first design
- Database support

**Commands**:
```bash
notionfs clone [URL]     # Clone workspace
notionfs pull            # Download changes
notionfs push            # Upload changes
notionfs sync            # Bidirectional sync
notionfs watch           # Continuous sync
```

**Workspace Structure**:
- `.notionfs/` for config and state
- Pages as `.md` files
- Directories for parent pages
- YAML frontmatter for DB properties

**PyPI Package**: `notionfs`

**Unique Features**:
- Watch mode
- Multiple conflict resolution strategies
- Clean workspace structure
- Offline-first philosophy

**Limitations**:
- Small community (12 stars)
- Limited documentation
- Relatively new

---

### 6. notion-sync (Adjective-Object)
- **URL**: https://github.com/Adjective-Object/notion-sync
- **Stars**: 27
- **Updated**: 2024-10-28 (stale)
- **Language**: Python
- **Type**: CLI tool

**Features**:
- Sync Notion to local markdown
- PyPI package: `notion-sync`

**Status**: Appears stale (last update Oct 2024)

---

## Category 4: Notion → Obsidian Migration Tools

### 7. notoma
- **URL**: https://github.com/natikgadzhi/notoma
- **Stars**: 58
- **Updated**: 2026-03-16
- **Language**: Go
- **Type**: CLI tool

**Features**:
- One-way sync: Notion → Obsidian
- Incremental updates (modified since last run)
- Database → Obsidian Bases conversion
- Attachment handling
- Rate limiting

**Sync Direction**: One-way (Notion → Obsidian)

**Target Audience**: Users migrating from Notion to Obsidian

**Unique Aspects**:
- Obsidian-specific format
- `.base` file support
- Focus on regular ongoing incremental updates

**Not suitable for**: Editing locally and syncing back to Notion

---

### 8. SyncNos
- **URL**: https://github.com/chiimagnus/SyncNos
- **Stars**: 68
- **Updated**: 2026-03-27
- **Language**: TypeScript
- **Type**: Browser extension

**Features**:
- Capture AI chats from 11+ platforms
- Capture web articles
- Local-first storage (IndexedDB)
- Sync to Notion or Obsidian
- Export as Markdown/Zip

**Sync Direction**: One-way (Browser → Notion/Obsidian)

**Target Audience**: AI conversation archival, not general Notion editing

**Unique Aspects**:
- Browser extension
- AI chat focus
- Multiple AI platforms supported
- Local-first with incremental sync

**Not suitable for**: General Notion page editing

---

### 9. Notion-2-Obsidian
- **URL**: https://github.com/visualcurrent/Notion-2-Obsidian
- **Stars**: 273
- **Updated**: 2026-02-27
- **Language**: Python

**Features**:
- Convert Notion exports to Obsidian format
- Fix Notion markdown quirks for Obsidian compatibility

**Type**: Conversion tool for migration, not continuous sync

---

## Category 5: Backup Tools

### 10. notion-export-client
- **URL**: https://github.com/delta1037/notion-export-client
- **Stars**: 156
- **Updated**: 2026-03-25
- **Language**: JavaScript
- **Type**: Backup client

**Features**:
- One-way backup: Notion → Local markdown
- Self-structured export
- Chinese and English documentation

**Use Case**: Periodic backups, not editing workflow

---

### 11. Notion-Backup
- **URL**: https://github.com/IRHM/Notion-Backup
- **Stars**: 20
- **Updated**: 2023-10-16 (stale)
- **Language**: Go

**Features**:
- Download all Notion notes as markdown
- Optional git backup

**Status**: Appears abandoned

---

## Category 6: GitHub Actions / CI Tools

### 12. notion-github-action
- **URL**: https://github.com/tryfabric/notion-github-action
- **Stars**: 101
- **Updated**: 2026-03-25
- **Language**: TypeScript

**Features**:
- Sync GitHub issues → Notion database
- GitHub Action

**Use Case**: Issue tracking integration

---

### 13. notion-to-github-sync-action
- **URL**: https://github.com/novuhq/notion-to-github-sync-action
- **Stars**: 7
- **Updated**: 2026-03-06
- **Language**: JavaScript

**Features**:
- Sync Notion pages → GitHub markdown files
- GitHub Action

**Sync Direction**: One-way (Notion → GitHub)

---

## npm Packages Summary

| Package | Downloads | Purpose |
|---------|-----------|---------|
| `notion-to-md` | High | Conversion library |
| `@notionhq/client` | Very High | Official Notion API client |
| `@notionhq/notion-mcp-server` | Medium | MCP server for AI tools |
| `@tryfabric/martian` | Medium | Markdown → Notion blocks |
| `notion-types` | High | TypeScript types |
| `react-notion-x` | High | React renderer |

---

## Key Gaps in Existing Tools

1. **No dominant local-first sync solution**
   - Most tools are one-way (Notion → Local)
   - Few bidirectional tools are small/new projects

2. **Limited Claude Code integration**
   - Official plugin uses MCP (API access), not local sync
   - nsync is the only Claude Skill with true sync

3. **Obsidian gets more attention**
   - Many Notion→Obsidian tools
   - Obsidian has native sync, so less need for DIY solutions

4. **Focus on migration vs. continuous workflow**
   - Most tools designed for one-time migration
   - Few tools optimize for daily editing workflow

5. **Conflict resolution not mature**
   - Most bidirectional tools have basic conflict detection
   - No sophisticated merge strategies

---

## Comparison Table: Bidirectional Sync Tools

| Tool | Stars | Language | Updated | Sync | Claude | Conflicts | Media | DB Support |
|------|-------|----------|---------|------|--------|-----------|-------|------------|
| **nsync** | 1 | Python | 2026-03-27 | ✅ Bi | ✅ Yes | Manual | ✅ Yes | ✅ SQLite |
| **notionfs** | 12 | Python | 2026-03-26 | ✅ Bi | ❌ No | Multi-strategy | ✅ Yes | ✅ Yes |
| **notion-sync** | 27 | Python | 2024-10-28 | ❌ One-way | ❌ No | N/A | ❓ ? | ❓ ? |
| **notoma** | 58 | Go | 2026-03-16 | ❌ One-way | ❌ No | N/A | ✅ Yes | ✅ Obsidian |

---

## Recommendations for Your Project

### If Building a New Tool:

**Differentiation Opportunities**:
1. **Claude Code native experience** - Most tools are CLI-first
2. **Smart conflict resolution** - Current tools require manual resolution
3. **Rich block preservation** - Many tools lose formatting in round-trips
4. **Database ergonomics** - SQLite is good, but UX could be better
5. **Workspace management** - Multi-workspace, selective sync

**Learn From**:
- **nsync**: Claude Skill integration, clean Python implementation
- **notionfs**: Workspace structure, offline-first design
- **notion-to-md**: Format flexibility, community adoption
- **Official plugin**: MCP integration patterns

**Avoid**:
- Obsidian-specific formats (limits audience)
- One-way sync only (many tools already do this)
- Complex dependencies (Python stdlib approach is elegant)

### If Using Existing Tools:

**For Claude Code Integration**:
- **Option 1**: Official plugin (best for API access, not local editing)
- **Option 2**: nsync (best for local markdown sync, very new)
- **Option 3**: Build skill wrapper around notionfs

**For General Use**:
- **Bidirectional**: notionfs (more mature than nsync)
- **Backup**: notion-export-client (popular, well-maintained)
- **Migration**: notoma (if going to Obsidian)

---

## Technical Patterns Observed

### Common Architecture:
1. **Sync State Tracking**
   - Local DB (SQLite, JSON) to track sync state
   - Content hashing for change detection
   - Timestamp comparison for conflicts

2. **Workspace Structure**
   - Hidden `.notion*/` or `_sync/` directory
   - Markdown files with YAML frontmatter
   - `_assets/` for media files

3. **API Usage**
   - Official `@notionhq/client` or direct REST
   - Rate limiting with exponential backoff
   - Batch operations for efficiency

4. **Conflict Resolution**
   - Timestamp comparison (local vs remote)
   - Content hash comparison
   - Manual resolution prompts
   - Some tools offer "ours" vs "theirs" strategies

### Notion API Challenges:
- Rate limits (429 responses)
- Pagination for large workspaces
- Block type coverage (some blocks not well supported)
- Media file handling (temporary URLs)
- Database property type mapping

---

## Market Observations

1. **Fragmentation**: No clear winner in bidirectional sync space
2. **Recency**: Many projects created in 2024-2026 (growing interest)
3. **Languages**: Python and TypeScript dominate
4. **Stars Distribution**: Long tail (most projects < 100 stars)
5. **Maintenance**: Many stale projects (last updated 2023-2024)
6. **Claude Code**: Emerging space, few mature tools

**Opportunity**: A well-designed, Claude Code-native, bidirectional sync tool could become the standard if:
- Excellent UX
- Reliable conflict resolution
- Strong Claude Code integration
- Good documentation
- Active maintenance

---

## Related Searches Performed

- "notion markdown sync"
- "notion local sync"
- "notion git sync"
- "notion backup markdown"
- "notion-to-md"
- "claude code notion"
- "obsidian notion sync"

**GitHub Search Results**: ~100+ repositories analyzed
**npm Packages**: ~15 relevant packages identified
**PyPI Packages**: 2 relevant packages identified

---

## Conclusion

The Notion markdown sync landscape is **young and fragmented**. While conversion libraries like `notion-to-md` are mature, true bidirectional sync tools are sparse and mostly small projects.

**Key Takeaway**: There is a clear opportunity for a **polished, Claude Code-native, bidirectional sync tool** that balances local-first editing with reliable Notion synchronization.

The official Notion plugin takes a different approach (MCP/API access), leaving room for a complementary tool focused on local markdown workflows.
