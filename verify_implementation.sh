#!/bin/bash
# Final verification script for NotionSync implementation

echo "============================================"
echo "NotionSync Implementation Verification"
echo "============================================"
echo ""

# Check files exist
echo "1. Checking files..."
FILES=(
    "lib/notion_sync.py"
    "lib/__init__.py"
    "test_notion_sync.py"
    "docs/NOTION_SYNC_CLASS.md"
    "docs/QUICKSTART.md"
    "IMPLEMENTATION_SUMMARY.md"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file (missing)"
        exit 1
    fi
done

echo ""
echo "2. Testing imports..."
python3 -c "
from lib.notion_sync import NotionSync
from lib import NotionSync as NS
print('  ✓ Imports work')
" || exit 1

echo ""
echo "3. Running test suite..."
python3 test_notion_sync.py > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✓ All tests pass"
else
    echo "  ✗ Tests failed"
    exit 1
fi

echo ""
echo "4. Testing CLI interface..."
OUTPUT=$(python3 lib/notion_sync.py status 2>&1)
if echo "$OUTPUT" | grep -q '"files"'; then
    echo "  ✓ CLI works"
else
    echo "  ✗ CLI failed"
    exit 1
fi

echo ""
echo "5. Checking line count..."
LINES=$(wc -l < lib/notion_sync.py)
echo "  ✓ notion_sync.py: $LINES lines"

echo ""
echo "============================================"
echo "✓ All verification checks passed!"
echo "============================================"
echo ""
echo "Implementation complete and verified."
echo "Ready for production use."
