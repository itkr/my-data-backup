#!/bin/bash
# パッケージ状態チェック・修復スクリプト

echo "🔍 パッケージ状態をチェック中..."

# 仮想環境がアクティブかチェック
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ 仮想環境: $VIRTUAL_ENV"
else
    echo "❌ 仮想環境が非アクティブです"
    echo "💡 'source venv/bin/activate' を実行してください"
    exit 1
fi

# パッケージがインストールされているかチェック
if pip list | grep -q "my-data-backup"; then
    echo "✅ my-data-backup パッケージが見つかりました"
    pip show my-data-backup | grep "Location:"
else
    echo "❌ my-data-backup パッケージが見つかりません"
    echo "💡 'make install' または 'pip install -e .' を実行してください"
    exit 1
fi

# インポートテスト
python -c "
try:
    from src.core.services import MoveService
    print('✅ インポートテスト成功')
except ImportError as e:
    print(f'❌ インポートテスト失敗: {e}')
    print('💡 パッケージの再インストールが必要です')
    exit(1)
"

echo "🎉 パッケージは正常に動作しています"
