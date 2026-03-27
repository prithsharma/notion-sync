"""
Notion Sync utility library.

Provides core utilities for the notion-sync Python backend:
- hashing: SHA-256 content hashing
- frontmatter: YAML frontmatter parsing and serialization
- manifest: Sync state tracking and management
- notion_sync: Main orchestrator class
"""

from .hashing import compute_hash, hash_file
from .frontmatter import FrontmatterParser
from .manifest import ManifestManager
from .notion_sync import NotionSync

__all__ = [
    'compute_hash',
    'hash_file',
    'FrontmatterParser',
    'ManifestManager',
    'NotionSync',
]
