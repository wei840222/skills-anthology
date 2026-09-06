#!/usr/bin/env bash
# ==============================================================================
# AI Agent Skills Synchronization Script (sync.sh)
# Description: Automatically scans README.md for skill package paths and links
#              them directly to a specified target directory.
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/sync.py" "$@"
