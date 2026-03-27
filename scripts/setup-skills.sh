#!/bin/bash
# Setup script to install Notion Sync skills for Claude Code

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
SKILLS_DIR="${HOME}/.claude/skills"

echo "🔧 Setting up Notion Sync skills for Claude Code..."

# Check if Claude Code skills directory exists
if [ ! -d "$SKILLS_DIR" ]; then
  echo "❌ Claude Code skills directory not found at: $SKILLS_DIR"
  echo "   Please make sure Claude Code is installed."
  exit 1
fi

# Create symlinks for each skill
for skill in pull-notion push-notion notion-status; do
  source_dir="$REPO_ROOT/skills/$skill"
  target_dir="$SKILLS_DIR/$skill"

  # Remove existing skill if present
  if [ -L "$target_dir" ]; then
    echo "🔄 Removing existing symlink: $skill"
    rm "$target_dir"
  elif [ -d "$target_dir" ]; then
    echo "⚠️  Existing skill directory found: $skill"
    echo "   Moving to ${skill}.backup"
    mv "$target_dir" "${target_dir}.backup"
  fi

  # Create symlink
  echo "✅ Installing skill: $skill"
  ln -s "$source_dir" "$target_dir"
done

echo ""
echo "✨ Skills installed successfully!"
echo ""
echo "Available commands in Claude Code:"
echo "  /pull-notion <notion-url> [output-path]"
echo "  /push-notion <file-path> [--force]"
echo "  /notion-status [file-path] [--verbose]"
echo ""
echo "📚 See README.md for usage examples"
