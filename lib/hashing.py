"""
SHA-256 hashing utilities for content comparison.

Provides simple functions to compute SHA-256 hashes of strings and files.
Used for detecting changes in local and remote content.
"""

import hashlib
from pathlib import Path
from typing import Union


def compute_hash(content: str) -> str:
    """
    Compute SHA-256 hash of a string.

    Args:
        content: The string content to hash

    Returns:
        Hexadecimal string representation of the SHA-256 hash

    Example:
        >>> compute_hash("hello world")
        'b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9'
    """
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def hash_file(file_path: Union[str, Path]) -> str:
    """
    Compute SHA-256 hash of a file's content.

    Args:
        file_path: Path to the file to hash

    Returns:
        Hexadecimal string representation of the SHA-256 hash

    Raises:
        FileNotFoundError: If the file does not exist
        IOError: If the file cannot be read

    Example:
        >>> hash_file("path/to/file.md")
        'a1b2c3d4e5f6...'
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    # Read and hash file content
    content = path.read_text(encoding='utf-8')
    return compute_hash(content)
