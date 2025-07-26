#!/bin/bash
# Photo Organizer サンプルスクリプト - v2.0 開発可能パッケージ版

current_dir=$(cd $(dirname $0); pwd)
project_root="$(cd $(dirname $0)/.. && pwd)"

cd "${project_root}"
source ./venv/bin/activate

echo "🚀 Photo Organizer CLI (v2.0) を実行中..."
echo "📂 ソースディレクトリ: ${current_dir}"
echo "📁 出力ディレクトリ: ${current_dir}/organized"
echo ""

# 開発可能パッケージとしてインストール済みのため、PYTHONPATHの設定は不要
# パッケージが正しくインストールされているかチェック
if ! python -c "import src.core.services" 2>/dev/null; then
    echo "⚠️  パッケージが正しくインストールされていません"
    echo "🔧 make install を実行してください"
    exit 1
fi

# 出力ディレクトリを作成
mkdir -p "${current_dir}/organized"

# クリーンな実行（パス操作なし）
python src/main.py cli photo \
    --src="${current_dir}" \
    --dir="${current_dir}/organized" \
    --dry-run

echo ""
echo "✅ 実行完了！"
echo "💡 実際のファイル整理を行う場合は --dry-run オプションを削除してください"
