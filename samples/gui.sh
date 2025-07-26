#!/bin/bash
# 統合GUI サンプルスクリプト - v2.0 開発可能パッケージ版

project_root="$(cd $(dirname $0)/.. && pwd)"

cd "${project_root}"

echo "🚀 統合GUIアプリケーション (v2.0) を起動中..."
echo ""

# パッケージが正しくインストールされているかチェック
if ! python -c "import src.core.services" 2>/dev/null; then
    echo "⚠️  パッケージが正しくインストールされていません"
    echo "🔧 make install を実行してください"
    exit 1
fi

# Makefileのコマンドを使用（開発可能パッケージ対応済み）
make run-gui

echo ""
echo "✅ GUI起動完了！"
