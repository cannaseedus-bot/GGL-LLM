#!/bin/bash
# ========================================================
# Fetch Cline Library
# Downloads the cline-1.0.9.jar library file
# ========================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JAR_URL="https://mx2lm.app/cline-jars/lib/cline-1.0.9.jar"
JAR_FILE="$SCRIPT_DIR/cline-1.0.9.jar"

echo "Downloading cline-1.0.9.jar..."
curl -sSL -o "$JAR_FILE" "$JAR_URL"

if [ -f "$JAR_FILE" ]; then
    SIZE=$(stat -c%s "$JAR_FILE" 2>/dev/null || stat -f%z "$JAR_FILE" 2>/dev/null)
    echo "Downloaded successfully: $JAR_FILE ($SIZE bytes)"
else
    echo "Download failed"
    exit 1
fi
