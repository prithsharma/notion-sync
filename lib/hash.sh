#!/bin/bash
# Compute SHA-256 hash of content
# Usage: ./hash.sh <file> OR echo "content" | ./hash.sh

if [ -n "$1" ] && [ -f "$1" ]; then
  # Hash file content (excluding frontmatter for content hash)
  openssl dgst -sha256 -binary "$1" | xxd -p -c 256
else
  # Hash stdin
  openssl dgst -sha256 -binary | xxd -p -c 256
fi
