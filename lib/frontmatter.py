"""
YAML frontmatter parsing and serialization for markdown files.

Handles extraction and insertion of YAML frontmatter blocks in markdown
files using the standard --- delimiter format.
"""

import re
from typing import Dict, Tuple, Any


class FrontmatterParser:
    """
    Parse and serialize YAML frontmatter in markdown files.

    Frontmatter format:
        ---
        key: value
        another_key: another value
        ---

        # Markdown content here
    """

    # Regex pattern to match frontmatter block
    # Matches: ---\n(content)\n---\n(rest)
    FRONTMATTER_PATTERN = re.compile(
        r'^---\s*\n(.*?)\n---\s*\n(.*)$',
        re.DOTALL
    )

    @classmethod
    def parse(cls, content: str) -> Tuple[Dict[str, Any], str]:
        """
        Extract YAML frontmatter and body from markdown content.

        Args:
            content: Full markdown content with optional frontmatter

        Returns:
            Tuple of (frontmatter_dict, body_content)
            If no frontmatter exists, returns ({}, original_content)

        Example:
            >>> content = "---\\nkey: value\\n---\\n\\nBody text"
            >>> fm, body = FrontmatterParser.parse(content)
            >>> fm
            {'key': 'value'}
            >>> body
            'Body text'
        """
        match = cls.FRONTMATTER_PATTERN.match(content)

        if not match:
            # No frontmatter found
            return {}, content

        frontmatter_text = match.group(1)
        body = match.group(2).strip()

        # Parse YAML frontmatter (simple key: value parsing)
        frontmatter = cls._parse_yaml(frontmatter_text)

        return frontmatter, body

    @classmethod
    def serialize(cls, frontmatter: Dict[str, Any], body: str) -> str:
        """
        Combine frontmatter and body into markdown content.

        Args:
            frontmatter: Dictionary of frontmatter key-value pairs
            body: Markdown body content

        Returns:
            Complete markdown content with frontmatter block

        Example:
            >>> fm = {'key': 'value', 'number': 42}
            >>> body = 'Body text'
            >>> FrontmatterParser.serialize(fm, body)
            '---\\nkey: value\\nnumber: 42\\n---\\n\\nBody text'
        """
        if not frontmatter:
            # No frontmatter to add
            return body

        # Serialize frontmatter to YAML
        yaml_lines = []
        for key, value in frontmatter.items():
            yaml_lines.append(cls._serialize_yaml_line(key, value))

        yaml_text = '\n'.join(yaml_lines)

        # Combine with body
        return f"---\n{yaml_text}\n---\n\n{body}"

    @classmethod
    def _parse_yaml(cls, yaml_text: str) -> Dict[str, Any]:
        """
        Parse simple YAML content into a dictionary.

        Supports:
        - Simple key: value pairs
        - Strings, numbers, booleans, null
        - Quoted strings (preserves quotes are removed)

        Args:
            yaml_text: YAML content to parse

        Returns:
            Dictionary of parsed key-value pairs
        """
        result = {}

        for line in yaml_text.split('\n'):
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue

            # Parse key: value
            if ':' not in line:
                continue

            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()

            # Parse value type
            result[key] = cls._parse_yaml_value(value)

        return result

    @classmethod
    def _parse_yaml_value(cls, value: str) -> Any:
        """
        Parse a YAML value string into appropriate Python type.

        Args:
            value: String representation of value

        Returns:
            Parsed value (str, int, float, bool, or None)
        """
        # Handle empty/null
        if not value or value.lower() in ('null', '~'):
            return None

        # Handle booleans
        if value.lower() == 'true':
            return True
        if value.lower() == 'false':
            return False

        # Handle quoted strings
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            return value[1:-1]

        # Try to parse as number
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            pass

        # Return as string
        return value

    @classmethod
    def _serialize_yaml_line(cls, key: str, value: Any) -> str:
        """
        Serialize a key-value pair to YAML format.

        Args:
            key: The key name
            value: The value to serialize

        Returns:
            YAML line string (e.g., "key: value")
        """
        # Handle None
        if value is None:
            return f"{key}: null"

        # Handle booleans
        if isinstance(value, bool):
            return f"{key}: {str(value).lower()}"

        # Handle numbers
        if isinstance(value, (int, float)):
            return f"{key}: {value}"

        # Handle strings
        # Quote if contains special characters or starts/ends with whitespace
        value_str = str(value)
        if cls._needs_quoting(value_str):
            # Escape internal quotes
            escaped = value_str.replace('"', '\\"')
            return f'{key}: "{escaped}"'

        return f"{key}: {value_str}"

    @classmethod
    def _needs_quoting(cls, value: str) -> bool:
        """
        Check if a string value needs quoting in YAML.

        Args:
            value: String to check

        Returns:
            True if the value should be quoted
        """
        if not value:
            return True

        # Check for leading/trailing whitespace
        if value != value.strip():
            return True

        # Check for special YAML characters
        special_chars = [':', '#', '[', ']', '{', '}', ',', '&', '*', '!', '|', '>', '@', '`']
        if any(char in value for char in special_chars):
            return True

        # Check if looks like a boolean or null
        if value.lower() in ('true', 'false', 'null', 'yes', 'no', 'on', 'off'):
            return True

        return False
