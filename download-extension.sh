#!/usr/bin/env bash
# Download CDP Browse Bridge Chrome extension
# Usage: curl -sSL https://raw.githubusercontent.com/dave-wind/cdp-browse/master/download-extension.sh | bash

set -e

DEST="${1:-$(pwd)/cdp_browse_extension}"
REPO="https://gitee.com/dave-wind/cdp-browse-extenssion.git"
TMP=$(mktemp -d)

echo "Downloading CDP Browse Bridge extension..."
git clone --depth 1 "$REPO" "$TMP/repo"
cp -r "$TMP/repo/"* "$DEST/"
rm -rf "$TMP"

echo ""
echo "Done! Extension downloaded to: $DEST"
echo "Load it in Chrome:"
echo "  1. Open chrome://extensions/"
echo "  2. Enable Developer mode"
echo "  3. Click 'Load unpacked'"
echo "  4. Select: $DEST"
