#!/bin/bash
# Photo Organizer サンプルスクリプト - v2.0 新アーキテクチャ版

current_dir=$(cd $(dirname $0); pwd)
project_root="$(cd $(dirname $0)/.. && pwd)"

cd "${project_root}"
source ./venv/bin/activate

echo "🚀 Photo Organizer CLI (v2.0) を実行中..."
echo "📂 ソースディレクトリ: ${current_dir}"
echo "📁 出力ディレクトリ: ${current_dir}/organized"
echo ""

# 出力ディレクトリを作成
mkdir -p "${current_dir}/organized"

# v2.0 新アーキテクチャのコマンドを実行
cd src && PYTHONPATH="${project_root}" python main.py cli photo \
    --src="${current_dir}" \
    --dir="${current_dir}/organized" \
    --dry-run

echo ""
echo "✅ 実行完了！"
echo "💡 実際のファイル整理を行う場合は --dry-run オプションを削除してください"
