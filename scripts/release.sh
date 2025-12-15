#!/bin/bash

# GPTProto Dify Plugin Release Script
# This script automates the process of packaging and releasing the plugin
#
# Usage:
#   ./scripts/release.sh [version]
#
# Examples:
#   ./scripts/release.sh           # Interactive mode, asks for version
#   ./scripts/release.sh 0.0.18    # Use specified version

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Plugin info
PLUGIN_NAME="gptproto"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  GPTProto Dify Plugin Release Script  ${NC}"
echo -e "${BLUE}========================================${NC}"

# Function to print colored messages
info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# Change to project root
cd "$PROJECT_ROOT"
info "Working directory: $PROJECT_ROOT"

# Get current version from manifest.yaml
CURRENT_VERSION=$(grep "^version:" manifest.yaml | head -1 | awk '{print $2}')
info "Current version: $CURRENT_VERSION"

# Check if version is passed as argument
if [ -n "$1" ]; then
    NEW_VERSION="$1"
    info "Using version from argument: $NEW_VERSION"
else
    # Ask for new version or use current
    echo ""
    read -p "Enter new version (press Enter to keep $CURRENT_VERSION): " NEW_VERSION
    NEW_VERSION=${NEW_VERSION:-$CURRENT_VERSION}
fi

# Update version in manifest.yaml if changed
if [ "$NEW_VERSION" != "$CURRENT_VERSION" ]; then
    info "Updating version to $NEW_VERSION..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/^version: .*/version: $NEW_VERSION/" manifest.yaml
    else
        # Linux
        sed -i "s/^version: .*/version: $NEW_VERSION/" manifest.yaml
    fi
    success "Version updated to $NEW_VERSION"
fi

# Git operations
echo ""
info "Checking git status..."
if [ -n "$(git status --porcelain)" ]; then
    echo ""
    git status --short
    echo ""
    read -p "Do you want to commit all changes? (y/n): " COMMIT_CHANGES
    if [ "$COMMIT_CHANGES" = "y" ] || [ "$COMMIT_CHANGES" = "Y" ]; then
        read -p "Enter commit message (default: 'Release v$NEW_VERSION'): " COMMIT_MSG
        COMMIT_MSG=${COMMIT_MSG:-"Release v$NEW_VERSION"}

        git add .
        git commit -m "$COMMIT_MSG"
        success "Changes committed"
    fi
fi

# Create output directory
OUTPUT_DIR="$PROJECT_ROOT/dist"
mkdir -p "$OUTPUT_DIR"

# Package the plugin
echo ""
info "Packaging plugin..."
PACKAGE_FILE="$OUTPUT_DIR/${PLUGIN_NAME}-${NEW_VERSION}.difypkg"

# Check if dify CLI is available
if command -v dify &> /dev/null; then
    info "Using dify CLI to package..."
    dify plugin package "$PROJECT_ROOT" -o "$OUTPUT_DIR"

    # Find the generated package file
    GENERATED_PKG=$(ls -t "$OUTPUT_DIR"/*.difypkg 2>/dev/null | head -1)
    if [ -n "$GENERATED_PKG" ] && [ -f "$GENERATED_PKG" ]; then
        # Rename to include version if needed
        if [ "$GENERATED_PKG" != "$PACKAGE_FILE" ]; then
            mv "$GENERATED_PKG" "$PACKAGE_FILE" 2>/dev/null || PACKAGE_FILE="$GENERATED_PKG"
        fi
    fi
else
    # Manual packaging using zip (difypkg is essentially a zip file)
    info "dify CLI not found, using manual zip packaging..."

    # Create a temporary directory for packaging
    TEMP_DIR=$(mktemp -d)
    PLUGIN_DIR="$TEMP_DIR/$PLUGIN_NAME"
    mkdir -p "$PLUGIN_DIR"

    # Copy files to temp directory (excluding unnecessary files)
    rsync -av --progress "$PROJECT_ROOT/" "$PLUGIN_DIR/" \
        --exclude='.git' \
        --exclude='.gitignore' \
        --exclude='dist' \
        --exclude='scripts' \
        --exclude='dify' \
        --exclude='.env' \
        --exclude='.env.*' \
        --exclude='*.pyc' \
        --exclude='__pycache__' \
        --exclude='.DS_Store' \
        --exclude='*.difypkg' \
        --exclude='.claude' \
        --exclude='working' \
        --exclude='CLAUDE.md' \
        --exclude='GUIDE.md' \
        --exclude='.history' \
        2>/dev/null || true

    # Create the difypkg (zip file)
    cd "$TEMP_DIR"
    zip -r "$PACKAGE_FILE" "$PLUGIN_NAME" -x "*.DS_Store" -x "*__pycache__*"

    # Cleanup
    rm -rf "$TEMP_DIR"
    cd "$PROJECT_ROOT"
fi

# Verify package was created
if [ -f "$PACKAGE_FILE" ]; then
    PACKAGE_SIZE=$(du -h "$PACKAGE_FILE" | cut -f1)
    success "Plugin packaged: $PACKAGE_FILE ($PACKAGE_SIZE)"
else
    error "Failed to create package file"
fi

# Ask about creating git tag
echo ""
read -p "Do you want to create a git tag v$NEW_VERSION? (y/n): " CREATE_TAG
if [ "$CREATE_TAG" = "y" ] || [ "$CREATE_TAG" = "Y" ]; then
    if git rev-parse "v$NEW_VERSION" >/dev/null 2>&1; then
        warning "Tag v$NEW_VERSION already exists"
        read -p "Do you want to delete and recreate it? (y/n): " RECREATE_TAG
        if [ "$RECREATE_TAG" = "y" ] || [ "$RECREATE_TAG" = "Y" ]; then
            git tag -d "v$NEW_VERSION"
            git tag -a "v$NEW_VERSION" -m "Release v$NEW_VERSION"
            success "Tag v$NEW_VERSION recreated"
        fi
    else
        git tag -a "v$NEW_VERSION" -m "Release v$NEW_VERSION"
        success "Created tag v$NEW_VERSION"
    fi
fi

# Ask about pushing to remote
echo ""
read -p "Do you want to push to remote (including tags)? (y/n): " PUSH_REMOTE
if [ "$PUSH_REMOTE" = "y" ] || [ "$PUSH_REMOTE" = "Y" ]; then
    git push origin HEAD
    git push origin --tags
    success "Pushed to remote"
fi

# Summary
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}          Release Complete!            ${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Version:  $NEW_VERSION"
echo "Package:  $PACKAGE_FILE"
echo ""
info "Next steps:"
echo "  1. Upload $PACKAGE_FILE to Dify marketplace"
echo "  2. Or install locally: dify plugin install $PACKAGE_FILE"
echo ""
