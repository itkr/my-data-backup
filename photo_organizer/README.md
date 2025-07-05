# Photo Organizer

📸 RAWファイルとJPGファイルを整理するためのPythonツール

## 概要

Photo Organizerは、デジタルカメラで撮影したRAWファイルとJPGファイルを効率的に整理するためのツールです。JPGファイルの構造に合わせてRAWファイルを自動的に同期し、孤立したRAWファイルを管理できます。

## 主な機能

- 📁 **フォルダ構造同期**: JPGファイルのディレクトリ構造にRAWファイルを自動同期
- 🔍 **孤立ファイル管理**: 対応するJPGファイルが存在しないRAWファイルを自動検出・隔離
- 🎯 **GUI/CLI両対応**: グラフィカルインターフェースとコマンドラインの両方で利用可能
- 📝 **詳細ログ**: 処理結果を詳細にログ出力
- 🛡️ **ドライラン**: 実際の変更前に処理内容を確認可能
- 📋 **柔軟な操作**: ファイルの移動またはコピーを選択可能

## インストール

1. リポジトリをクローン:
```bash
git clone https://github.com/itkr/my-data-backup.git
cd my-data-backup
```

2. 依存関係をインストール:
```bash
pip install -r requirements.txt
```

## 使用方法

### GUI版の使用

```bash
cd photo_organizer
python gui.py
```

GUI版の特徴:
- 📊 **リアルタイム進捗**: 処理の進捗をリアルタイムで表示
- 📈 **統計情報**: ファイル数やディレクトリ情報を事前表示
- 🎨 **視覚的操作**: 直感的なインターフェース
- 📄 **ログ表示**: 処理結果をGUI内で確認

### CLI版の使用

```bash
cd photo_organizer
python main.py [オプション]
```

#### 基本的な使用例

```bash
# 基本的な同期（移動）
python main.py --root-dir /path/to/photos

# ドライラン（実行せずに確認）
python main.py --root-dir /path/to/photos --dry-run

# ファイルをコピー（移動しない）
python main.py --root-dir /path/to/photos --copy

# 孤立RAWファイルを隔離
python main.py --root-dir /path/to/photos --isolate-orphans

# ログファイルを作成
python main.py --root-dir /path/to/photos --log-file sync.log
```

#### オプション詳細

| オプション | 説明 | デフォルト |
|-----------|------|----------|
| `--root-dir` | 対象のルートディレクトリ | カレントディレクトリ |
| `--raw-dir` | RAWファイルのディレクトリ名 | `ARW` |
| `--jpg-dir` | JPGファイルのディレクトリ名 | `JPG` |
| `--raw-extensions` | RAW拡張子（カンマ区切り） | `.arw` |
| `--jpg-extensions` | JPG拡張子（カンマ区切り） | `.jpg` |
| `--copy` | ファイルをコピー（移動しない） | False |
| `--isolate-orphans` | 孤立RAWファイルを隔離 | False |
| `--dry-run` | 実行せずに確認のみ | False |
| `--log-file` | ログファイルのパス | なし |

## ディレクトリ構造

### 想定される入力構造

```
photos/
├── JPG/
│   ├── 2024/
│   │   ├── 01_January/
│   │   │   ├── IMG_001.jpg
│   │   │   └── IMG_002.jpg
│   │   └── 02_February/
│   │       └── IMG_003.jpg
│   └── 2025/
│       └── 01_January/
│           └── IMG_004.jpg
└── ARW/
    ├── IMG_001.arw
    ├── IMG_002.arw
    ├── IMG_003.arw
    ├── IMG_004.arw
    └── IMG_005.arw  # 孤立ファイル
```

### 処理後の構造

```
photos/
├── JPG/
│   ├── 2024/
│   │   ├── 01_January/
│   │   │   ├── IMG_001.jpg
│   │   │   └── IMG_002.jpg
│   │   └── 02_February/
│   │       └── IMG_003.jpg
│   └── 2025/
│       └── 01_January/
│           └── IMG_004.jpg
└── ARW/
    ├── 2024/
    │   ├── 01_January/
    │   │   ├── IMG_001.arw
    │   │   └── IMG_002.arw
    │   └── 02_February/
    │       └── IMG_003.arw
    ├── 2025/
    │   └── 01_January/
    │       └── IMG_004.arw
    └── orphans/
        └── IMG_005.arw  # 孤立ファイル
```

## 機能詳細

### 1. ファイル同期

- JPGファイルのディレクトリ構造を基準として、対応するRAWファイルを同じ構造に配置
- ファイル名の拡張子以外の部分でマッチング
- 大文字小文字を区別しない拡張子の処理

### 2. 孤立ファイル管理

- 対応するJPGファイルが存在しないRAWファイルを検出
- `--isolate-orphans`オプションで孤立ファイルを`orphans/`フォルダに移動
- 孤立ファイルのリスト表示

### 3. 安全機能

- **ドライラン**: 実際の変更前に処理内容を確認
- **事前検証**: ディレクトリの存在確認とファイル数の表示
- **詳細ログ**: すべての操作を記録
- **エラーハンドリング**: 適切なエラーメッセージと処理継続

### 4. GUI機能

- **リアルタイム進捗**: 処理の進捗をプログレスバーで表示
- **統計情報**: ファイル数やディレクトリ情報を事前表示
- **ログ表示**: 処理結果をGUI内でリアルタイム表示
- **設定保存**: 前回の設定を記憶

## 設定ファイル

`config.py`を使用してデフォルト設定をカスタマイズできます：

```python
DEFAULT_CONFIG = {
    "raw_dir": "ARW",
    "jpg_dir": "JPG", 
    "raw_extensions": [".arw"],
    "jpg_extensions": [".jpg", ".jpeg"],
    "orphan_dir": "orphans",
    "default_copy": False,
    "default_isolate_orphans": False,
    "default_dry_run": False,
}
```

## 対応ファイル形式

### RAWファイル
- `.arw` (Sony)
- `.cr2`, `.cr3` (Canon)
- `.nef` (Nikon)
- `.dng` (Adobe)
- その他のRAW形式（設定で追加可能）

### JPGファイル
- `.jpg`
- `.jpeg`
- その他の画像形式（設定で追加可能）

## トラブルシューティング

### よくある問題

1. **ファイルが見つからない**
   - ディレクトリパスが正しいか確認
   - ファイル拡張子の設定を確認

2. **権限エラー**
   - ファイルやディレクトリの権限を確認
   - 管理者権限で実行

3. **処理が遅い**
   - 大量のファイルがある場合は時間がかかることがあります
   - `--dry-run`でまず処理内容を確認

### ログの確認

```bash
# ログファイルを指定して実行
python main.py --root-dir /path/to/photos --log-file sync.log

# ログファイルの内容を確認
cat sync.log
```

## 開発

### 開発環境のセットアップ

```bash
# 開発用依存関係のインストール
pip install -r requirements.txt

# コードフォーマット
black photo_organizer/

# テスト実行
python -m pytest tests/
```

### プロジェクト構造

```
photo_organizer/
├── config.py              # 設定管理
├── logger.py              # ログ機能
├── gui.py                 # GUI版
└── main.py                # CLI版
```