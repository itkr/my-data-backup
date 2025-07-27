#!/bin/bash
# Move サンプルスクリプト - v2.0 開発可能パッケージ版

current_dir=$(cd $(dirname $0); pwd)
cd ~/Projects/github.com/itkr/my-data-backup
source ./venv/bin/activate

# 開発可能パッケージとしてインストール済みのため、PYTHONPATHの設定は不要
# パッケージが正しくインストールされているかチェック
if ! python -c "import src.core.services" 2>/dev/null; then
    echo "⚠️  パッケージが正しくインストールされていません"
    echo "🔧 make install を実行してください"
    exit 1
fi

# クリーンな実行（パス操作なし）
python src/main.py cli move \
    --import-dir="${current_dir}" \
    --export-dir="${current_dir}" \
    --no-recursive
