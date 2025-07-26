# 開発可能パッケージ（Development Package）の注意点

`pip install -e .`（開発可能インストール）を使用する際の重要な注意点とベストプラクティスをまとめます。

## 🔑 主要な注意点

### 1. ファイル変更の即座反映
- **利点**: Pythonファイルの変更が即座に反映される
- **注意**: 一度インポートされたモジュールは`importlib.reload()`が必要な場合がある
- **対処**: 実行中のプロセスを再起動することが推奨

### 2. インポートパスの管理
- **重要**: 開発パッケージ化により、相対インポートから絶対インポートに変更が必要
- **例**: `from ...core.services import` → `from src.core.services import`
- **確認**: `make check-package`でインポートエラーを検出

### 3. 仮想環境の依存性
- **必須**: 開発パッケージは特定の仮想環境に依存
- **リスク**: 環境が削除されるとパッケージも消失
- **対策**: `requirements.txt`と`pyproject.toml`で依存関係を明確化

### 4. editable-installsファイル
- **場所**: `venv/lib/python3.x/site-packages/`
- **内容**: パッケージのパスが記録される
- **注意**: このファイルが壊れるとインポートエラーが発生

## 🛠️ トラブルシューティング

### インポートエラーが発生した場合
```bash
# パッケージ状態をチェック
make check-package

# パッケージを再インストール
make reinstall

# 依存関係を確認
make list-packages
```

### よくある問題と解決法

#### 1. `ModuleNotFoundError`
**原因**: パッケージが正しくインストールされていない
**解決**: `make reinstall`

#### 2. `ImportError: attempted relative import`
**原因**: 相対インポートが残っている
**解決**: 絶対インポートに変更

#### 3. 古いコードが実行される
**原因**: Pythonプロセスでモジュールがキャッシュされている
**解決**: プロセスを再起動

## 📋 日常の開発ワークフロー

### 1. 新しい開発セッション開始時
```bash
# 仮想環境をアクティベート
make venv-activate

# パッケージ状態を確認
make check-package
```

### 2. コード変更後
```bash
# CLIツールのテスト
make test-cli

# GUIアプリケーションのテスト
make run-gui
```

### 3. 大きな変更後
```bash
# パッケージを再インストール
make reinstall

# すべてのテストを実行
make test-all
```

## 🔍 パッケージ状態の監視

### 自動チェックスクリプト
`scripts/check_package.sh`が以下を確認：
- パッケージのインストール状態
- 主要モジュールのインポート可能性
- パッケージのバージョン情報

### 定期的な確認
```bash
# 毎日の開発開始時
make check-package

# パッケージ一覧の確認
make list-packages
```

## 🚨 エラー対応

### 緊急時の復旧手順
1. `make clean` - 一時ファイルをクリーンアップ
2. `make venv-clean` - 仮想環境を再作成
3. `make install` - パッケージを再インストール
4. `make check-package` - 状態を確認

### ログの確認
- エラーが発生した場合は詳細なログを確認
- `make run-gui`や`make test-cli`の出力をチェック

## 💡 ベストプラクティス

1. **定期的な状態確認**: 開発セッション開始時に`make check-package`
2. **クリーンな環境**: 問題が発生したら仮想環境の再作成を検討
3. **バージョン管理**: `pyproject.toml`でバージョンを適切に管理
4. **依存関係の明示**: 新しい依存関係は必ず`pyproject.toml`に追加

## 🔗 関連コマンド

| コマンド | 用途 |
|---------|------|
| `make install` | 開発可能パッケージのインストール |
| `make check-package` | パッケージ状態のチェック |
| `make reinstall` | パッケージの再インストール |
| `make list-packages` | インストール済みパッケージの確認 |
| `make venv-clean` | 仮想環境のリセット |

この開発可能パッケージ方式により、`PROJECT_ROOT`のような動的パス設定が不要になり、より標準的で保守しやすいPythonプロジェクト構造を実現できます。
