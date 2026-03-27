#!/usr/bin/env node

/**
 * Notion Sync Library
 * Core utilities for syncing markdown files with Notion pages
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const SYNC_DIR = path.join(process.env.HOME, 'os', '.notion-sync');
const MANIFEST_PATH = path.join(SYNC_DIR, 'manifest.json');
const BLOCKS_DIR = path.join(SYNC_DIR, 'blocks');
const CONFIG_PATH = path.join(SYNC_DIR, 'config.json');

// ============================================================================
// Manifest Operations
// ============================================================================

/**
 * Read the manifest file
 * @returns {Object} Manifest data
 */
function readManifest() {
  if (!fs.existsSync(MANIFEST_PATH)) {
    return {
      default_database: null,
      files: {}
    };
  }
  return JSON.parse(fs.readFileSync(MANIFEST_PATH, 'utf8'));
}

/**
 * Write the manifest file
 * @param {Object} manifest - Manifest data
 */
function writeManifest(manifest) {
  fs.writeFileSync(MANIFEST_PATH, JSON.stringify(manifest, null, 2), 'utf8');
}

/**
 * Get file entry from manifest
 * @param {string} filePath - Path to local file
 * @returns {Object|null} File entry or null if not found
 */
function getFileEntry(filePath) {
  const manifest = readManifest();
  return manifest.files[filePath] || null;
}

/**
 * Update file entry in manifest
 * @param {string} filePath - Path to local file
 * @param {Object} entry - File entry data
 */
function updateFileEntry(filePath, entry) {
  const manifest = readManifest();
  manifest.files[filePath] = {
    ...manifest.files[filePath],
    ...entry
  };
  writeManifest(manifest);
}

/**
 * Remove file entry from manifest
 * @param {string} filePath - Path to local file
 */
function removeFileEntry(filePath) {
  const manifest = readManifest();
  delete manifest.files[filePath];
  writeManifest(manifest);
}

/**
 * List all synced files
 * @returns {Array<{path: string, entry: Object}>}
 */
function listSyncedFiles() {
  const manifest = readManifest();
  return Object.entries(manifest.files).map(([path, entry]) => ({
    path,
    entry
  }));
}

// ============================================================================
// Config Operations
// ============================================================================

/**
 * Read config file
 * @returns {Object} Config data
 */
function readConfig() {
  if (!fs.existsSync(CONFIG_PATH)) {
    return {
      default_parent: null,
      conflict_strategy: 'ask' // 'ask', 'local', 'notion', 'newer'
    };
  }
  return JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
}

/**
 * Write config file
 * @param {Object} config - Config data
 */
function writeConfig(config) {
  fs.writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2), 'utf8');
}

// ============================================================================
// Frontmatter Operations
// ============================================================================

/**
 * Parse frontmatter from markdown content
 * @param {string} content - Markdown content
 * @returns {{frontmatter: Object, content: string}}
 */
function parseFrontmatter(content) {
  const match = content.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  if (!match) {
    return { frontmatter: {}, content };
  }

  const frontmatterText = match[1];
  const bodyContent = match[2];

  // Simple YAML parser for our needs
  const frontmatter = {};
  frontmatterText.split('\n').forEach(line => {
    const colonIndex = line.indexOf(':');
    if (colonIndex > 0) {
      const key = line.substring(0, colonIndex).trim();
      let value = line.substring(colonIndex + 1).trim();

      // Remove quotes if present
      if ((value.startsWith('"') && value.endsWith('"')) ||
          (value.startsWith("'") && value.endsWith("'"))) {
        value = value.slice(1, -1);
      }

      // Parse booleans
      if (value === 'true') value = true;
      if (value === 'false') value = false;

      frontmatter[key] = value;
    }
  });

  return { frontmatter, content: bodyContent };
}

/**
 * Serialize frontmatter to YAML string
 * @param {Object} frontmatter - Frontmatter object
 * @returns {string} YAML string
 */
function serializeFrontmatter(frontmatter) {
  const lines = Object.entries(frontmatter).map(([key, value]) => {
    if (typeof value === 'string' && (value.includes(':') || value.includes('#'))) {
      return `${key}: "${value}"`;
    }
    return `${key}: ${value}`;
  });
  return `---\n${lines.join('\n')}\n---\n`;
}

/**
 * Read markdown file with frontmatter
 * @param {string} filePath - Path to markdown file
 * @returns {{frontmatter: Object, content: string, fullContent: string}}
 */
function readMarkdownFile(filePath) {
  const fullContent = fs.readFileSync(filePath, 'utf8');
  const { frontmatter, content } = parseFrontmatter(fullContent);
  return { frontmatter, content, fullContent };
}

/**
 * Write markdown file with frontmatter
 * @param {string} filePath - Path to markdown file
 * @param {Object} frontmatter - Frontmatter object
 * @param {string} content - Markdown content
 */
function writeMarkdownFile(filePath, frontmatter, content) {
  const frontmatterStr = serializeFrontmatter(frontmatter);
  const fullContent = frontmatterStr + content;
  fs.writeFileSync(filePath, fullContent, 'utf8');
}

// ============================================================================
// Hash Operations
// ============================================================================

/**
 * Compute hash of content
 * @param {string} content - Content to hash
 * @returns {string} SHA256 hash
 */
function hashContent(content) {
  return crypto.createHash('sha256').update(content, 'utf8').digest('hex');
}

/**
 * Check if local file has been modified since last sync
 * @param {string} filePath - Path to local file
 * @returns {boolean}
 */
function isLocalModified(filePath) {
  const entry = getFileEntry(filePath);
  if (!entry) return true;

  const { content } = readMarkdownFile(filePath);
  const currentHash = hashContent(content);
  return currentHash !== entry.local_hash;
}

// ============================================================================
// Rich Block Operations
// ============================================================================

const RICH_BLOCK_PATTERNS = [
  /<details[\s>]/,  // toggles
  /<callout/,       // callouts
  /<table/,         // tables
  /<columns/,       // columns
  /<synced_block/,  // synced blocks
  /<meeting-notes/, // meeting notes
];

/**
 * Detect if content has rich Notion blocks
 * @param {string} content - Markdown content
 * @returns {boolean}
 */
function hasRichBlocks(content) {
  return RICH_BLOCK_PATTERNS.some(pattern => pattern.test(content));
}

/**
 * Save rich blocks for a page
 * @param {string} pageId - Notion page ID
 * @param {Object} blocks - Blocks data from Notion API
 */
function saveRichBlocks(pageId, blocks) {
  const blockPath = path.join(BLOCKS_DIR, `${pageId}.json`);
  fs.writeFileSync(blockPath, JSON.stringify(blocks, null, 2), 'utf8');
}

/**
 * Load rich blocks for a page
 * @param {string} pageId - Notion page ID
 * @returns {Object|null} Blocks data or null if not found
 */
function loadRichBlocks(pageId) {
  const blockPath = path.join(BLOCKS_DIR, `${pageId}.json`);
  if (!fs.existsSync(blockPath)) return null;
  return JSON.parse(fs.readFileSync(blockPath, 'utf8'));
}

// ============================================================================
// Status Operations
// ============================================================================

/**
 * Get sync status for a file
 * @param {string} filePath - Path to local file
 * @returns {string} Status: 'not_synced', 'synced', 'local_modified', 'conflict', 'notion_only'
 */
function getSyncStatus(filePath) {
  const entry = getFileEntry(filePath);

  if (!entry) {
    return 'not_synced';
  }

  // Check if file exists locally
  if (!fs.existsSync(filePath)) {
    return 'notion_only';
  }

  const { content } = readMarkdownFile(filePath);
  const currentHash = hashContent(content);

  if (currentHash !== entry.local_hash) {
    // Local has changed - need to check if Notion also changed
    if (entry.notion_hash_at_sync !== entry.notion_hash) {
      return 'conflict';
    }
    return 'local_modified';
  }

  return 'synced';
}

/**
 * Get sync status for all files
 * @returns {Array<{path: string, status: string, entry: Object}>}
 */
function getAllSyncStatus() {
  const files = listSyncedFiles();
  return files.map(({ path, entry }) => ({
    path,
    status: getSyncStatus(path),
    entry
  }));
}

// ============================================================================
// Exports
// ============================================================================

module.exports = {
  // Constants
  SYNC_DIR,
  MANIFEST_PATH,
  BLOCKS_DIR,
  CONFIG_PATH,

  // Manifest operations
  readManifest,
  writeManifest,
  getFileEntry,
  updateFileEntry,
  removeFileEntry,
  listSyncedFiles,

  // Config operations
  readConfig,
  writeConfig,

  // Frontmatter operations
  parseFrontmatter,
  serializeFrontmatter,
  readMarkdownFile,
  writeMarkdownFile,

  // Hash operations
  hashContent,
  isLocalModified,

  // Rich block operations
  hasRichBlocks,
  saveRichBlocks,
  loadRichBlocks,

  // Status operations
  getSyncStatus,
  getAllSyncStatus,
};
