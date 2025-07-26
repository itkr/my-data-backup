# Code Formatting & Import Management

## 🎯 概要

このプロジェクトでは、import文の整理とコードフォーマットにおいて、複数のツールを**統一された順序**で実行することで一貫性を保っています。

## 🔧 使用ツール

| ツール | 役割 | 実行順序 |
|--------|------|----------|
| **autoflake** | 未使用import削除・変数整理 | 1️⃣ |
| **isort** | import並び替え・グループ化 | 2️⃣ |
| **black** | コード全体のフォーマット | 3️⃣ |
| **flake8** | 品質チェック・検証 | 4️⃣ |

## ⚡ 推奨コマンド

### 統一フォーマット（推奨）
```bash
make format-unified
```

このコマンドは以下を順番に実行します：
1. autoflakeで未使用importを削除
2. isortでimportを整理
3. blackでコード全体をフォーマット
4. flake8で結果を検証

### 個別実行
```bash
# importのみ整理
make format-imports

# blackのみ実行
make format

# 品質チェックのみ
make lint
```

## 📋 設定詳細

### pyproject.toml設定

```toml
[tool.black]
line-length = 88
target-version = ["py38"]

[tool.isort]
profile = "black"           # blackと互換性を保つ
line_length = 88
src_paths = ["src"]
known_first_party = ["src"]

[tool.autoflake]
remove-all-unused-imports = true
remove-unused-variables = true
ignore-init-module-imports = true
```

### .flake8設定

```ini
[flake8]
max-line-length = 88        # blackと統一
exclude = venv/, legacy/, __pycache__
```

## 🔍 トラブルシューティング

### 問題：ツール間でimport順序が異なる

**原因**: 各ツールの設定が統一されていない

**解決策**: 
1. pyproject.tomlの統一設定を使用
2. `make format-unified`で正しい順序で実行

### 問題：blackとisortの競合

**原因**: line-lengthやスタイル設定の不一致

**解決策**: 
- isortで`profile = "black"`を使用
- 両方で`line_length = 88`を統一

### 問題：autoflakeが必要なimportを削除

**原因**: 実際は使用されているが検出されない

**解決策**: 
- `# noqa`コメントで保護
- `ignore-init-module-imports = true`を設定

## 🎯 ベストプラクティス

1. **コミット前**: 必ず`make format-unified`を実行
2. **CI/CD**: 自動チェックに`make lint`を組み込み
3. **エディタ設定**: IDE/エディタでblack/isortを自動実行
4. **チーム開発**: 全員が同じpyproject.toml設定を使用

## 📈 効果

- ✅ **一貫性**: 全ファイルで統一されたimport順序
- ✅ **効率性**: 1コマンドで完全なフォーマット
- ✅ **品質**: 未使用importの自動削除
- ✅ **保守性**: 設定ファイルで一元管理
