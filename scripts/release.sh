#!/bin/bash

# GPTProto Dify Plugin Release Script
# This script automates the process of packaging and releasing the plugin

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

# Check if dify CLI is installed
if ! command -v dify &> /dev/null; then
    error "dify CLI not found. Please install it first: pip install dify-plugin-daemon"
fi

# Get current version from manifest.yaml
CURRENT_VERSION=$(grep "^version:" manifest.yaml | head -1 | awk '{print $2}')
info "Current version: $CURRENT_VERSION"

# Ask for new version or use current
echo ""
read -p "Enter new version (press Enter to keep $CURRENT_VERSION): " NEW_VERSION
NEW_VERSION=${NEW_VERSION:-$CURRENT_VERSION}

# Update version in manifest.yaml if changed
if [ "$NEW_VERSION" != "$CURRENT_VERSION" ]; then
    info "Updating version to $NEW_VERSION..."
    sed -i.bak "s/^version: .*/version: $NEW_VERSION/" manifest.yaml
    rm -f manifest.yaml.bak
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

# Use dify CLI to package
dify plugin package "$PROJECT_ROOT" -o "$OUTPUT_DIR"

# Find the generated package file
GENERATED_PKG=$(ls -t "$OUTPUT_DIR"/*.difypkg 2>/dev/null | head -1)
if [ -n "$GENERATED_PKG" ] && [ -f "$GENERATED_PKG" ]; then
    # Rename to include version if needed
    if [ "$GENERATED_PKG" != "$PACKAGE_FILE" ]; then
        mv "$GENERATED_PKG" "$PACKAGE_FILE" 2>/dev/null || PACKAGE_FILE="$GENERATED_PKG"
    fi
    success "Plugin packaged: $PACKAGE_FILE"
else
    error "Failed to create package file"
fi

# Ask about creating git tag
echo ""
read -p "Do you want to create a git tag v$NEW_VERSION? (y/n): " CREATE_TAG
if [ "$CREATE_TAG" = "y" ] || [ "$CREATE_TAG" = "Y" ]; then
    if git rev-parse "v$NEW_VERSION" >/dev/null 2>&1; then
        warning "Tag v$NEW_VERSION already exists"
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
info "To upload to Dify marketplace, use:"
echo "  dify plugin publish $PACKAGE_FILE"
echo ""
