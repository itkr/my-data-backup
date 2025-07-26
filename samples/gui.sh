#!/bin/bash
# 統合GUI サンプルスクリプト - v2.0 新アーキテクチャ版

project_root="$(cd $(dirname $0)/.. && pwd)"

cd "${project_root}"

echo "🚀 統合GUIアプリケーション (v2.0) を起動中..."
echo ""

# Makefileのコマンドを使用
make run-gui

echo ""
echo "✅ GUI起動完了！"
