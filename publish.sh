#!/usr/bin/env bash
# Publish cdp-browse to PyPI
#
# Prerequisites:
#   export UV_PUBLISH_TOKEN=pypi-xxx   # set in ~/.zshrc or ~/.bashrc
#
# Usage:
#   ./publish.sh              # uses UV_PUBLISH_TOKEN env var
#   ./publish.sh --token xxx  # pass token directly

set -e

echo "==> Cleaning old dist files..."
rm -rf dist/

echo "==> Building source distribution and wheel..."
uv build

echo "==> Publishing to PyPI..."
uv publish dist/* "$@"

echo "==> Done. Published:"
ls -lh dist/
