#!/bin/bash
set -e

# Full desktop build: PyInstaller backend → Tauri app → installer
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== Building cscode desktop app ==="

# Step 1: Build the PyInstaller backend binary
echo ""
echo ">>> Step 1: Building server binary..."
bash "$SCRIPT_DIR/build-server.sh"

# Step 2: Build Tauri desktop app
echo ""
echo ">>> Step 2: Building Tauri desktop app..."
cd "$PROJECT_DIR/desktop"
npm ci 2>/dev/null || true
npx tauri build

echo ""
echo "=== Build complete ==="
echo "Installers are in:"
echo "  $PROJECT_DIR/desktop/src-tauri/target/release/bundle/"
