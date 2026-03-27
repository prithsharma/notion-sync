# Publishing to GitHub

Quick guide to publish this repository to GitHub.

## Prerequisites

- GitHub account
- Git configured with your credentials

## Steps

### 1. Create GitHub Repository

Go to [github.com/new](https://github.com/new) and create a new repository:

**Settings:**
- **Name**: `notion-sync`
- **Description**: `Local-first Notion sync for Claude Code. Edit markdown locally, sync to Notion when ready.`
- **Visibility**: Public (or Private if preferred)
- **Initialize**: Leave unchecked (we already have files)

### 2. Add Remote

```bash
cd ~/os/notion-sync

# Add GitHub as remote
git remote add origin https://github.com/YOUR_USERNAME/notion-sync.git

# Or using SSH:
git remote add origin git@github.com:YOUR_USERNAME/notion-sync.git
```

### 3. Push to GitHub

```bash
# Push main branch
git push -u origin main
```

### 4. Update URLs in Files

Update the following files with your actual GitHub username:

**README.md:**
```markdown
- Homepage: https://github.com/YOUR_USERNAME/notion-sync
- Issues: https://github.com/YOUR_USERNAME/notion-sync/issues
- Clone: git clone https://github.com/YOUR_USERNAME/notion-sync.git
```

**package.json:**
```json
{
  "homepage": "https://github.com/YOUR_USERNAME/notion-sync#readme",
  "bugs": {
    "url": "https://github.com/YOUR_USERNAME/notion-sync/issues"
  },
  "repository": {
    "type": "git",
    "url": "git+https://github.com/YOUR_USERNAME/notion-sync.git"
  }
}
```

**CONTRIBUTING.md, docs/SETUP.md:**
- Update all github.com/yourusername references

**Then commit and push:**
```bash
git add README.md package.json CONTRIBUTING.md docs/
git commit -m "Update GitHub URLs"
git push
```

### 5. Configure GitHub Repository

**Settings → General:**
- Add topics: `notion`, `sync`, `markdown`, `claude-code`, `local-first`
- Add website: `https://claude.ai/code`

**Settings → Pages:**
- Enable GitHub Pages (optional)
- Source: Deploy from main branch

**Settings → Discussions:**
- Enable Discussions

### 6. Add Issue Templates

Create `.github/ISSUE_TEMPLATE/`:

**Bug report:**
```bash
mkdir -p .github/ISSUE_TEMPLATE
cat > .github/ISSUE_TEMPLATE/bug_report.md << 'EOF'
---
name: Bug report
about: Report a bug or issue
title: '[BUG] '
labels: bug
assignees: ''
---

**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce:
1. Pull page with '/pull-notion ...'
2. Edit file '...'
3. Push with '/push-notion ...'
4. See error

**Expected behavior**
What you expected to happen.

**Environment:**
- Claude Code version:
- Notion MCP version:
- OS:

**Logs/Screenshots**
Any error messages or screenshots.
EOF
```

**Feature request:**
```bash
cat > .github/ISSUE_TEMPLATE/feature_request.md << 'EOF'
---
name: Feature request
about: Suggest a new feature
title: '[FEATURE] '
labels: enhancement
assignees: ''
---

**Feature description**
Clear description of the feature.

**Use case**
Why do you need this feature?

**Proposed solution**
How should it work?

**Alternatives considered**
Other ways you considered solving this.
EOF
```

Commit and push:
```bash
git add .github/ISSUE_TEMPLATE/
git commit -m "Add issue templates"
git push
```

### 7. Add Labels

Go to **Issues → Labels** and create:
- `bug` - Something isn't working (red)
- `enhancement` - New feature or request (green)
- `documentation` - Documentation improvements (blue)
- `good first issue` - Good for newcomers (purple)
- `help wanted` - Extra attention needed (orange)
- `question` - Questions or clarifications (pink)

### 8. Create Release

**Option 1: Via GitHub UI**
1. Go to **Releases → Create a new release**
2. **Tag**: `v0.1.0`
3. **Title**: `Initial Release v0.1.0`
4. **Description**:
   ```markdown
   First public release of Notion Sync for Claude Code!

   ## Features
   - 🔄 Bidirectional sync between local markdown and Notion
   - ⚡ Local-first, session-based workflow
   - 🎨 Rich block preservation (toggles, callouts, tables, columns)
   - 🔀 Conflict detection with 3-way merge
   - 👥 Team-friendly with git-tracked manifest

   ## Installation
   See [Setup Guide](docs/SETUP.md)

   ## Quick Start
   ```bash
   git clone https://github.com/YOUR_USERNAME/notion-sync.git
   cd notion-sync
   ./scripts/setup-skills.sh
   ```

   Then in Claude Code:
   ```
   /pull-notion <notion-url> docs/file.md
   # Edit locally
   /push-notion docs/file.md
   ```

   ## Documentation
   - [README](README.md)
   - [Setup Guide](docs/SETUP.md)
   - [Per-Project State](docs/per-project-state.md)
   - [Contributing](CONTRIBUTING.md)
   ```
5. **Publish release**

**Option 2: Via Git**
```bash
git tag -a v0.1.0 -m "Initial release v0.1.0"
git push origin v0.1.0
```

Then create release on GitHub from the tag.

### 9. Add README Badges (Optional)

Add to top of README.md:

```markdown
# Notion Sync for Claude Code

[![GitHub release](https://img.shields.io/github/v/release/YOUR_USERNAME/notion-sync)](https://github.com/YOUR_USERNAME/notion-sync/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub issues](https://img.shields.io/github/issues/YOUR_USERNAME/notion-sync)](https://github.com/YOUR_USERNAME/notion-sync/issues)
[![GitHub stars](https://img.shields.io/github/stars/YOUR_USERNAME/notion-sync)](https://github.com/YOUR_USERNAME/notion-sync/stargazers)
```

### 10. Share!

**Places to share:**
- Reddit: r/notion, r/ClaudeAI
- Twitter/X: Tag @anthropic, @NotionHQ
- Hacker News: Show HN
- Product Hunt: Submit as product
- Notion community forums
- Claude Code community (if exists)

**Post template:**
```
🚀 Just released Notion Sync for Claude Code!

Edit Notion pages as markdown locally, sync when ready.

Features:
✓ Bidirectional sync
✓ Conflict detection
✓ Rich block preservation
✓ Team-friendly (git-tracked)
✓ Local-first workflow

https://github.com/YOUR_USERNAME/notion-sync

Feedback welcome!
```

## Post-Publish Tasks

### Documentation
- [ ] Add video demo to README
- [ ] Create usage examples
- [ ] Write blog post
- [ ] Record screen capture

### Community
- [ ] Respond to issues within 24-48h
- [ ] Welcome first-time contributors
- [ ] Tag good first issues

### Maintenance
- [ ] Set up GitHub Actions CI (already done!)
- [ ] Add tests
- [ ] Monitor for security issues
- [ ] Keep dependencies updated

## Promoting the Project

### Write Articles
- "Local-first Notion editing with Claude Code"
- "How we built bidirectional Notion sync"
- "Collaborating on Notion docs with git"

### Create Content
- YouTube demo video
- GIF showing pull → edit → push workflow
- Tweet thread explaining the problem/solution

### Engage Community
- Join Notion community Slack/Discord
- Share in Claude Code discussions
- Answer questions on Reddit/StackOverflow

## Analytics (Optional)

Track usage via:
- GitHub stars/forks
- GitHub traffic stats
- npm downloads (if published)

## Future

- [ ] Publish to npm registry
- [ ] Create VSCode extension
- [ ] Add to Claude Code marketplace (if exists)
- [ ] Build web demo/playground

---

**Ready to share your work with the world! 🚀**
