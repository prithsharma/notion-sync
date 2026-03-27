"""
Manifest file management for tracking sync state.

Manages the manifest.json file that tracks the sync state of all
markdown files, including Notion IDs, hashes, and sync timestamps.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any


class ManifestManager:
    """
    Manage manifest.json file for tracking file sync state.

    The manifest structure:
    {
        "default_database": "notion_database_id" or null,
        "files": {
            "path/to/file.md": {
                "notion_id": "abc123",
                "last_synced": "2026-03-28T10:30:00Z",
                "local_hash": "sha256...",
                "notion_hash": "sha256...",
                "notion_hash_at_sync": "sha256..."
            }
        }
    }
    """

    def __init__(self, manifest_path: Path):
        """
        Initialize ManifestManager with path to manifest file.

        Args:
            manifest_path: Path to the manifest.json file
        """
        self.manifest_path = Path(manifest_path)
        self._ensure_manifest_exists()

    def _ensure_manifest_exists(self) -> None:
        """
        Ensure manifest file exists, create with default structure if not.
        """
        if not self.manifest_path.exists():
            # Create parent directories if needed
            self.manifest_path.parent.mkdir(parents=True, exist_ok=True)

            # Write default manifest structure
            default_manifest = {
                "default_database": None,
                "files": {}
            }
            self.write(default_manifest)

    def read(self) -> Dict[str, Any]:
        """
        Read the entire manifest file.

        Returns:
            Dictionary containing the full manifest data

        Raises:
            json.JSONDecodeError: If manifest file contains invalid JSON
        """
        with open(self.manifest_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def write(self, data: Dict[str, Any]) -> None:
        """
        Write the entire manifest file.

        Args:
            data: Dictionary containing the full manifest data

        Raises:
            IOError: If the file cannot be written
        """
        with open(self.manifest_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write('\n')  # Add trailing newline

    def get_entry(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get the manifest entry for a specific file.

        Args:
            file_path: Path to the file (relative or absolute)

        Returns:
            Dictionary containing the file's manifest entry, or None if not found
        """
        manifest = self.read()
        return manifest.get("files", {}).get(file_path)

    def update_entry(self, file_path: str, entry: Dict[str, Any]) -> None:
        """
        Update or create a manifest entry for a file.

        Args:
            file_path: Path to the file (relative or absolute)
            entry: Dictionary containing the entry data to store

        Example:
            >>> manager.update_entry("docs/file.md", {
            ...     "notion_id": "abc123",
            ...     "last_synced": "2026-03-28T10:30:00Z",
            ...     "local_hash": "sha256...",
            ...     "notion_hash": "sha256...",
            ...     "notion_hash_at_sync": "sha256..."
            ... })
        """
        manifest = self.read()

        # Ensure files dict exists
        if "files" not in manifest:
            manifest["files"] = {}

        # Update entry
        manifest["files"][file_path] = entry

        self.write(manifest)

    def remove_entry(self, file_path: str) -> None:
        """
        Remove a manifest entry for a file.

        Args:
            file_path: Path to the file (relative or absolute)

        Note:
            Does nothing if the entry doesn't exist
        """
        manifest = self.read()

        # Remove entry if it exists
        if "files" in manifest and file_path in manifest["files"]:
            del manifest["files"][file_path]
            self.write(manifest)

    def list_all(self) -> List[Dict[str, Any]]:
        """
        List all manifest entries with file paths included.

        Returns:
            List of dictionaries, each containing the entry data
            plus a "file_path" key

        Example:
            >>> entries = manager.list_all()
            >>> for entry in entries:
            ...     print(entry["file_path"], entry["notion_id"])
        """
        manifest = self.read()
        files = manifest.get("files", {})

        entries = []
        for file_path, entry in files.items():
            # Create a copy of the entry with file_path added
            entry_with_path = {"file_path": file_path, **entry}
            entries.append(entry_with_path)

        return entries

    def find_by_notion_id(self, notion_id: str) -> Optional[Dict[str, Any]]:
        """
        Find a manifest entry by Notion page ID.

        Args:
            notion_id: The Notion page ID to search for

        Returns:
            Dictionary containing the entry data plus "file_path" key,
            or None if not found

        Example:
            >>> entry = manager.find_by_notion_id("abc123")
            >>> if entry:
            ...     print(f"Found at: {entry['file_path']}")
        """
        manifest = self.read()
        files = manifest.get("files", {})

        for file_path, entry in files.items():
            if entry.get("notion_id") == notion_id:
                return {"file_path": file_path, **entry}

        return None

    def get_default_database(self) -> Optional[str]:
        """
        Get the default Notion database ID.

        Returns:
            The default database ID string, or None if not set
        """
        manifest = self.read()
        return manifest.get("default_database")

    def set_default_database(self, database_id: Optional[str]) -> None:
        """
        Set the default Notion database ID.

        Args:
            database_id: The Notion database ID to set as default,
                        or None to clear the default
        """
        manifest = self.read()
        manifest["default_database"] = database_id
        self.write(manifest)
