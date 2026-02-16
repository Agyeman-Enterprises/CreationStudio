#!/bin/bash
# Creation Studio Launcher (Mac/Linux)
STUDIO_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$STUDIO_DIR"

echo "Starting Creation Studio..."

# Activate venv
source studio-venv/bin/activate

# Wait for server then open browser
(while ! curl -s http://127.0.0.1:7860 > /dev/null 2>&1; do sleep 1; done && open "http://127.0.0.1:7860" 2>/dev/null || xdg-open "http://127.0.0.1:7860" 2>/dev/null) &

python studio_app.py
