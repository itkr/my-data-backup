#!/bin/bash
# Move サンプルスクリプト - v2.0 新アーキテクチャ版

current_dir=$(cd $(dirname $0); pwd)
project_root="$(cd $(dirname $0)/.. && pwd)"

cd "${project_root}"
source ./venv/bin/activate

echo "🚀 Move CLI (v2.0) を実行中..."
echo "📂 インポートディレクトリ: ${current_dir}"
echo "📁 エクスポートディレクトリ: ${current_dir}"
echo ""

# v2.0 新アーキテクチャのコマンドを実行
cd src && PYTHONPATH="${project_root}" python main.py cli move \
    --import-dir="${current_dir}" \
    --export-dir="${current_dir}" \
    --dry-run

echo ""
echo "✅ 実行完了！"
echo "💡 実際のファイル移動を行う場合は --dry-run オプションを削除してください"
