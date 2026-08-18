#!/bin/bash

# Docker GUI アプリケーション起動スクリプト
# macOS と Linux で GUI アプリケーションを Docker で動作させるためのスクリプト

set -e

# カラー出力
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE} Docker GUI Setup Script${NC}"
echo "=============================="

# OS判定
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
else
    echo -e "${RED} Unsupported OS: $OSTYPE${NC}"
    exit 1
fi

echo -e " Detected OS: ${GREEN}$OS${NC}"

# macOS の場合: XQuartz のチェックと設定
if [[ "$OS" == "macOS" ]]; then
    echo -e "${YELLOW} macOS detected - Setting up XQuartz...${NC}"

    # XQuartz がインストールされているかチェック
    if ! command -v xquartz &> /dev/null; then
        echo -e "${RED} XQuartz is not installed.${NC}"
        echo -e "${YELLOW} Please install XQuartz:${NC}"
        echo "brew install --cask xquartz"
        echo "# or download from https://www.xquartz.org/"
        exit 1
    fi

    echo -e "${GREEN} XQuartz found${NC}"

    # XQuartz を起動
    echo "Starting XQuartz..."
    open -a XQuartz

    # X11フォワーディングを許可
    echo "Configuring X11 forwarding..."
    xhost +localhost

    # DISPLAY環境変数を設定
    export DISPLAY=host.docker.internal:0

    echo -e "${GREEN} macOS X11 setup complete${NC}"
    echo -e "   DISPLAY=${DISPLAY}"

# Linux の場合
elif [[ "$OS" == "Linux" ]]; then
    echo -e "${YELLOW} Linux detected - Setting up X11...${NC}"

    # X11フォワーディングを許可
    echo "Allowing X11 forwarding..."
    xhost +local:docker

    # DISPLAY環境変数を確認
    if [[ -z "$DISPLAY" ]]; then
        export DISPLAY=:0
    fi

    echo -e "${GREEN} Linux X11 setup complete${NC}"
    echo -e "   DISPLAY=${DISPLAY}"
fi

# Dockerコンテナが存在するかチェック
echo ""
echo "Checking Docker setup..."

if ! docker ps -a --format "table {{.Names}}" | grep -q "my-data-backup-gui"; then
    echo -e "${YELLOW} Building Docker image...${NC}"
    docker-compose build my-data-backup-gui
fi

# GUI用コンテナを起動
echo -e "${BLUE} Starting GUI container...${NC}"
docker-compose up -d my-data-backup-gui

echo ""
echo -e "${GREEN} Setup complete!${NC}"
echo ""
echo -e "${BLUE} Available GUI commands:${NC}"
echo "docker exec -it my-data-backup-gui python photo_organizer/gui.py"
echo "docker exec -it my-data-backup-gui python move/gui.py"
echo ""
echo -e "${BLUE} CLI commands:${NC}"
echo "docker exec -it my-data-backup-gui make run-photo-organizer"
echo "docker exec -it my-data-backup-gui make run-move"
echo ""
echo -e "${YELLOW} Tip: Place your files in ./data/ directory to access them from the container${NC}"

# GUI起動オプションの提供
echo ""
read -p " Do you want to start Photo Organizer GUI now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${GREEN} Starting Photo Organizer GUI...${NC}"
    docker exec -it my-data-backup-gui python photo_organizer/gui.py
fi
