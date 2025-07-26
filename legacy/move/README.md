# File Organizer

ファイルを日付・拡張子ごとに自動整理するPythonスクリプトです。

## 機能

- 📁 ファイルを日付・拡張子ごとに整理
- 🔄 重複ファイルの自動処理
- 📝 ログ出力機能
- 🏃 ドライランモード
- 📊 処理結果の統計表示

## インストール

```bash
pip install click
```

## 使用方法

### Makefileを使用（推奨）

#### GUI版の実行
```bash
# プロジェクトルートから
make run-move-gui
```

#### CLI版の実行
```bash
# プロジェクトルートから
make run-move SRC=/path/to/source DEST=/path/to/destination

# 例
make run-move SRC=~/Downloads DEST=~/Documents/Organized
```

### 直接Pythonで実行

#### 基本的な使用方法

```bash
# プロジェクトルートから実行
PYTHONPATH=/path/to/my-data-backup python move/main.py --import-dir /path/to/source --export-dir /path/to/destination
```

### オプション

| オプション | 説明 | デフォルト |
|-----------|------|----------|
| `--import-dir` | 整理元ディレクトリ | 現在のディレクトリ |
| `--export-dir` | 整理先ディレクトリ | "export" |
| `--suffix` | 特定の拡張子のみ処理 | 全対応拡張子 |
| `--dry-run` | 実際の移動を行わず、処理内容を表示 | False |
| `--log-file` | ログファイルのパス | なし |
| `--verbose` | 詳細な出力 | False |

### 使用例

#### 1. Makefileを使用（推奨）

```bash
# GUI版で実行
make run-move-gui

# CLI版で実行
make run-move SRC=./photos DEST=./organized

# ドライランで確認（直接Python実行）
PYTHONPATH=$(pwd) python move/main.py --import-dir ./photos --export-dir ./organized --dry-run
```

#### 2. 直接Python実行（プロジェクトルートから）

```bash
# ドライランで処理内容を確認
PYTHONPATH=$(pwd) python move/main.py --import-dir ./photos --export-dir ./organized --dry-run
```

#### 3. 特定の拡張子のみ処理

```bash
PYTHONPATH=$(pwd) python move/main.py --import-dir ./photos --export-dir ./organized --suffix jpg
```

#### 4. ログ出力付きで実行

```bash
PYTHONPATH=$(pwd) python move/main.py --import-dir ./photos --export-dir ./organized --log-file organize.log --verbose
```

### Docker での実行

```bash
# GUI版
make docker-run-move-gui

# CLI版
make docker-run-move
```

## ディレクトリ構造

整理後のファイルは以下の構造で保存されます：

```
export_dir/
├── 2024/
│   ├── 01月/
│   │   ├── 2024-01-15/
│   │   │   ├── jpg/
│   │   │   │   ├── IMG_001.jpg
│   │   │   │   └── IMG_002.jpg
│   │   │   └── arw/
│   │   │       ├── IMG_001.arw
│   │   │       └── IMG_002.arw
│   │   └── 2024-01-16/
│   │       └── mp4/
│   │           └── VIDEO_001.mp4
│   └── 02月/
│       └── ...
└── 2025/
    └── ...
```

## 対応ファイル形式

### 画像ファイル
- JPEG, JPG, PNG, GIF, BMP, HIF, ARW

### 動画ファイル
- MOV, MP4, MPG, MTS, LRF, LRV

### 音声ファイル
- WAV, MP3

### その他
- XML, PSD

## 特徴

### 重複ファイル処理
- 同じファイル名・サイズの場合：スキップ
- 同じファイル名・異なるサイズの場合：タイムスタンプ付きでリネーム

### エラーハンドリング
- ファイルアクセスエラーの適切な処理
- 詳細なエラーメッセージ
- ログファイルへのエラー記録

### 安全性
- ドライランモードで事前確認
- 移動前の存在確認
- 例外処理による安全な実行

## 改善点

元のスクリプトから以下の改善を行いました：

1. **エラーハンドリング強化**
   - ファイル存在確認
   - 重複ファイル処理
   - 詳細なエラーメッセージ

2. **機能追加**
   - ドライランモード
   - ログ出力
   - 進捗表示
   - 統計情報

3. **コード品質向上**
   - 型ヒント追加
   - Pathlibの使用
   - より良い例外処理
   - ドキュメントの充実

4. **使いやすさ向上**
   - 詳細なヘルプメッセージ
   - カラー出力
   - 進捗状況の表示

## トラブルシューティング

### よくある問題

1. **Permission Error**
   - ファイルの読み取り・書き込み権限を確認
   - 管理者権限で実行

2. **FileNotFoundError**
   - 指定したディレクトリが存在することを確認
   - 相対パスではなく絶対パスを使用

3. **Disk Space Error**
   - 十分な空き容量があることを確認
   - 大きなファイルの場合は事前に確認

### ログファイルの確認

```bash
# ログファイルの内容を確認
tail -f organize.log

# エラーのみを確認
grep "ERROR" organize.log
```