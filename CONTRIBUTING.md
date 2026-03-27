# Contributing to Notion Sync

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful, inclusive, and constructive in all interactions.

## How to Contribute

### Reporting Bugs

**Before submitting:**
1. Check [existing issues](https://github.com/yourusername/notion-sync/issues)
2. Verify you're using the latest version
3. Test with a minimal reproduction case

**When submitting:**
- Use the bug report template
- Include:
  - Claude Code version
  - Notion MCP version
  - Steps to reproduce
  - Expected vs actual behavior
  - Error messages or logs
  - Screenshots if relevant

### Suggesting Features

**Before submitting:**
1. Check [existing discussions](https://github.com/yourusername/notion-sync/discussions)
2. Consider if it fits the project scope (local-first sync)

**When submitting:**
- Use the feature request template
- Include:
  - Clear use case
  - Why existing features don't solve it
  - Proposed API/interface
  - Willingness to implement

### Pull Requests

**Process:**

1. **Fork and clone**
   ```bash
   git clone https://github.com/yourusername/notion-sync.git
   cd notion-sync
   git remote add upstream https://github.com/original/notion-sync.git
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow existing code style
   - Add tests if applicable
   - Update documentation

4. **Test locally**
   ```bash
   # Install skills
   ./scripts/setup-skills.sh

   # Test in Claude Code
   /pull-notion <test-url>
   /push-notion <test-file>
   ```

5. **Commit with clear messages**
   ```bash
   git commit -m "Add: feature description"
   git commit -m "Fix: bug description"
   git commit -m "Docs: documentation updates"
   ```

6. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then open PR on GitHub.

**PR Guidelines:**

- **Title**: Clear, concise description
- **Description**: Explain what and why
  - What problem does it solve?
  - How does it solve it?
  - Breaking changes?
  - Related issues?
- **Tests**: Add tests for new features
- **Docs**: Update README, docs/ if needed
- **Size**: Keep PRs focused and reviewable

## Development Setup

### Requirements

- Node.js 18+
- Claude Code installed
- Notion MCP configured
- Git

### Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/notion-sync.git
cd notion-sync

# Link skills for testing
./scripts/setup-skills.sh

# Make changes to skills/ or lib/

# Test in Claude Code
# Open Claude Code and use /pull-notion, /push-notion, etc.
```

### Project Structure

```
notion-sync/
├── lib/               # Core library code
│   ├── sync-lib.js   # Main sync logic
│   └── hash.sh       # Hashing utility
├── skills/            # Claude Code skills
│   ├── pull-notion/
│   ├── push-notion/
│   └── notion-status/
├── scripts/           # Setup and utility scripts
├── docs/              # Documentation
├── examples/          # Example projects
└── tests/             # Tests (future)
```

### Testing

**Manual testing:**

1. Create a test Notion page
2. Test pull:
   ```bash
   /pull-notion <test-url> test/file.md
   ```
3. Edit test/file.md
4. Test push:
   ```bash
   /push-notion test/file.md
   ```
5. Verify in Notion
6. Test conflict detection (edit both sides)

**Automated tests (future):**
```bash
npm test
```

### Documentation

When adding features:

- Update README.md with usage examples
- Update relevant docs/ files
- Add example to examples/ if applicable
- Update skills/*.md with new parameters

## Code Style

### General

- Use clear, descriptive names
- Add comments for complex logic
- Keep functions focused and small
- Prefer clarity over cleverness

### JavaScript

```javascript
// Use const/let, not var
const filePath = 'docs/file.md';

// Use descriptive names
function updateManifestEntry(filePath, entry) {
  // ...
}

// Document complex functions
/**
 * Detect conflicts between local and Notion content
 * @param {string} filePath - Path to local file
 * @returns {boolean} True if conflict detected
 */
function detectConflict(filePath) {
  // ...
}
```

### Markdown (skills)

```markdown
# Clear, action-oriented headings

Use:
- Bullet points for lists
- Code blocks with syntax highlighting
- Examples for clarity

**Bold** for emphasis, *italic* sparingly.
```

### Bash (scripts)

```bash
#!/bin/bash
# Script description

set -e  # Exit on error

# Clear variable names
SKILLS_DIR="${HOME}/.claude/skills"

# Check prerequisites
if [ ! -d "$SKILLS_DIR" ]; then
  echo "Error: Skills directory not found"
  exit 1
fi
```

## Areas for Contribution

### High Priority

- **Tests**: Add automated tests
- **Error handling**: Improve error messages
- **Conflict resolution**: Better merge tools
- **Documentation**: More examples, guides

### Features

- Bulk sync (`/sync-notion --all`)
- Watch mode (auto-push on save)
- Interactive merge tool
- Template support
- CLI tool (use outside Claude Code)

### Nice to Have

- Bidirectional link tracking
- Notion database sync
- Rich block editor helpers
- Performance optimizations

## Questions?

- **General questions**: [GitHub Discussions](https://github.com/yourusername/notion-sync/discussions)
- **Bug reports**: [GitHub Issues](https://github.com/yourusername/notion-sync/issues)
- **Feature requests**: [GitHub Discussions](https://github.com/yourusername/notion-sync/discussions/categories/ideas)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
