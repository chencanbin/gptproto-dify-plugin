#!/bin/bash

# GPTProto Dify Plugin 自动发布脚本
# 使用方法: ./scripts/release.sh [版本号]
# 示例: ./scripts/release.sh 0.0.5

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 获取脚本所在目录的父目录（项目根目录）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PARENT_DIR="$(dirname "$PROJECT_DIR")"

cd "$PROJECT_DIR"

# 检查是否安装了 gh CLI
if ! command -v gh &> /dev/null; then
    echo -e "${RED}错误: 需要安装 GitHub CLI (gh)${NC}"
    echo "安装方法: brew install gh"
    echo "然后运行: gh auth login"
    exit 1
fi

# 检查 gh 是否已登录
if ! gh auth status &> /dev/null; then
    echo -e "${RED}错误: GitHub CLI 未登录${NC}"
    echo "请运行: gh auth login"
    exit 1
fi

# 获取版本号
if [ -z "$1" ]; then
    # 从 manifest.yaml 读取当前版本
    CURRENT_VERSION=$(grep "^version:" manifest.yaml | head -1 | awk '{print $2}')
    echo -e "${YELLOW}当前版本: $CURRENT_VERSION${NC}"
    echo -n "请输入新版本号 (留空使用当前版本): "
    read INPUT_VERSION
    VERSION=${INPUT_VERSION:-$CURRENT_VERSION}
else
    VERSION=$1
fi

# 确保版本号格式正确
if [[ ! $VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo -e "${RED}错误: 版本号格式不正确，应为 x.y.z 格式${NC}"
    exit 1
fi

TAG="v$VERSION"

echo -e "${GREEN}准备发布版本: $TAG${NC}"

# 更新 manifest.yaml 中的版本号
echo "更新 manifest.yaml 版本号..."
sed -i '' "s/^version: .*/version: $VERSION/" manifest.yaml
sed -i '' "s/version: [0-9]*\.[0-9]*\.[0-9]*/version: $VERSION/" manifest.yaml

# 检查是否有未提交的更改
if [[ -n $(git status -s) ]]; then
    echo "提交更改..."
    git add -A
    git commit -m "chore: bump version to $VERSION"
fi

# 推送到远程
echo "推送到 GitHub..."
git push origin main

# 删除已存在的同名 tag（如果有）
if git tag -l | grep -q "^$TAG$"; then
    echo "删除已存在的 tag: $TAG"
    git tag -d "$TAG" 2>/dev/null || true
    git push origin ":refs/tags/$TAG" 2>/dev/null || true
fi

# 创建新 tag
echo "创建 tag: $TAG"
git tag "$TAG"
git push origin "$TAG"

# 打包插件
echo "打包插件..."
DIFY_CLI="/tmp/dify-plugin"

# 检查 dify-plugin CLI 是否存在
if [ ! -f "$DIFY_CLI" ]; then
    echo "下载 Dify Plugin CLI..."
    curl -L -o "$DIFY_CLI" https://github.com/langgenius/dify-plugin-daemon/releases/download/0.5.1/dify-plugin-darwin-arm64
    chmod +x "$DIFY_CLI"
fi

# 打包
cd "$PARENT_DIR"
rm -f gptproto-dify-plugin.difypkg
"$DIFY_CLI" plugin package ./gptproto-dify-plugin

PKG_FILE="$PARENT_DIR/gptproto-dify-plugin.difypkg"

if [ ! -f "$PKG_FILE" ]; then
    echo -e "${RED}错误: 打包失败${NC}"
    exit 1
fi

echo -e "${GREEN}打包成功: $PKG_FILE${NC}"

# 删除已存在的 release（如果有）
if gh release view "$TAG" &>/dev/null; then
    echo "删除已存在的 release: $TAG"
    gh release delete "$TAG" --yes
fi

# 创建 GitHub Release 并上传文件
echo "创建 GitHub Release..."
cd "$PROJECT_DIR"
gh release create "$TAG" \
    --title "$TAG" \
    --notes "## GPTProto Image Generation Plugin $TAG

### Features
- Text to Image generation using GPTProto Gemini-3-Pro API
- Support multiple sizes (1K, 2K)
- Support multiple aspect ratios (1:1, 3:2, 2:3, 16:9, 9:16)
- Support multiple output formats (PNG, JPG, WebP)

### Installation
1. Download the \`.difypkg\` file
2. Go to Dify Plugin page
3. Click 'Install Plugin' -> 'Local Upload'
4. Upload the downloaded file
5. Configure your GPTProto API Key" \
    "$PKG_FILE"

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}发布成功! ${NC}"
echo -e "${GREEN}版本: $TAG${NC}"
echo -e "${GREEN}Release URL: https://github.com/chencanbin/gptproto-dify-plugin/releases/tag/$TAG${NC}"
echo -e "${GREEN}============================================${NC}"
