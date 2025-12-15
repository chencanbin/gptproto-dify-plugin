#!/bin/bash

set -e

cd "$(dirname "$0")/.."

# Get current version from manifest.yaml
VERSION=$(grep "^version:" manifest.yaml | head -1 | sed 's/version: //')
echo "Current version: $VERSION"

# Increment patch version (e.g., 0.0.1 -> 0.0.2)
IFS='.' read -r major minor patch <<< "$VERSION"
patch=$((patch + 1))
NEW_VERSION="${major}.${minor}.${patch}"
echo "New version: $NEW_VERSION"

# Update version in manifest.yaml (both top-level and meta.version)
sed -i '' "s/^version: .*/version: $NEW_VERSION/" manifest.yaml
sed -i '' "s/^  version: .*/  version: $NEW_VERSION/" manifest.yaml

# Create dist directory if not exists
mkdir -p dist

# Package name
PACKAGE_NAME="gptproto-tools-${NEW_VERSION}.difypkg"

# Remove old package if exists
rm -f "dist/${PACKAGE_NAME}"

# Create package using Dify CLI
echo "Packaging with Dify CLI..."
dify plugin package . -o "dist/${PACKAGE_NAME}"

echo ""
echo "Package created: dist/${PACKAGE_NAME}"
echo ""
echo "Done!"
