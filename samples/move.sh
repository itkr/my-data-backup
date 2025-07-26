#!/bin/bash
# Move サンプルスクリプト - v2.0 新アーキテクチャ版

current_dir=$(cd $(dirname $0); pwd)
cd ~/Projects/github.com/itkr/my-data-backup
source ./venv/bin/activate

# PYTHONPATHを設定してプロジェクトルートを追加
export PYTHONPATH=$(pwd):$PYTHONPATH

cd src && PYTHONPATH="${project_root}" python main.py cli move \
    --import-dir=${current_dir} \
    --export-dir=${current_dir} \
    --dry-run

