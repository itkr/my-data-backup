#!/bin/bash
current_dir=$(cd $(dirname $0); pwd)
cd ~/Projects/github.com/itkr/my-data-backup
source ./venv/bin/activate

# PYTHONPATHを設定してプロジェクトルートを追加
export PYTHONPATH=$(pwd):$PYTHONPATH

python ./move/main.py \
    --import-dir=${current_dir} \
    --export-dir=${current_dir}
