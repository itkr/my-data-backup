# My Data Backup

📁 RAW/JPG ファイルの整理と管理を効率化するツール集

## 🚀 概要

このプロジェクトは、デジタルカメラで撮影した RAW/JPG ファイルを効率的に整理・管理するための Python ツール集です。GUI と CLI の両方のインターフェースを提供し、ファイルの日付・拡張子ごとの自動整理や、RAW/JPG ファイルの同期処理を行います。

## 🎯 主な機能

### 📸 Photo Organizer
- **RAW/JPG ファイルの同期処理**
- **ファイルの移動・コピー・削除**
- **孤立ファイルの管理**
- **ドライランモードでの事前確認**
- **ログ機能付き**

### 🗂️ Move
- **日付・拡張子ごとのファイル整理**
- **複数のファイル形式に対応**（画像、動画、音声、ドキュメント等）
- **重複ファイルの自動処理**
- **進捗表示付きの処理**

## 📦 プロジェクト構造

```
my-data-backup/
├── Makefile              # 開発環境の自動化
├── README.md             # このファイル
├── requirements.txt      # Python 依存パッケージ
├── venv/                 # Python 仮想環境
├── photo_organizer/      # Photo Organizer ツール
│   ├── main.py          # CLI インターフェース
│   ├── gui.py           # GUI インターフェース
│   ├── config.py        # 設定ファイル
│   └── logger.py        # ログ機能
└── move/                 # Move ツール
    ├── main.py          # CLI インターフェース
    └── gui.py           # GUI インターフェース
```

## 🛠️ セットアップ

### 前提条件
- Python 3.8 以上
- macOS / Linux
- Git

### 1. リポジトリのクローン
```bash
git clone <repository-url>
cd my-data-backup
```

### 2. 開発環境の構築
```bash
# 仮想環境の作成と依存パッケージのインストール
make setup
```

### 3. 環境確認
```bash
# 環境情報の表示
make info
```

## 🎮 使用方法

### GUI での使用

#### Photo Organizer GUI
```bash
make run-photo-organizer
```

#### Move GUI
```bash
make run-move
```

### CLI での使用

#### Photo Organizer CLI
```bash
# 基本的な使用方法
make photo-cli SRC=/path/to/source DIR=/path/to/output

# 実際の例
make photo-cli SRC=~/Pictures/Camera DIR=~/Pictures/Organized
```

#### Move CLI
```bash
# 基本的な使用方法
make move-cli SRC=/path/to/source DEST=/path/to/destination

# 実際の例
make move-cli SRC=~/Downloads DEST=~/Documents/Organized
```

## 📋 Makefile コマンド一覧

### 🔧 環境構築
| コマンド | 説明 |
|----------|------|
| `make setup` | 開発環境の初期セットアップ |
| `make venv` | 仮想環境の作成 |
| `make install` | 依存パッケージのインストール |
| `make clean-venv` | 仮想環境の再作成 |

### 🚀 アプリケーション実行
| コマンド | 説明 |
|----------|------|
| `make run-photo-organizer` | Photo Organizer GUI を起動 |
| `make run-move` | Move GUI を起動 |
| `make photo-cli SRC=<path> DIR=<path>` | Photo Organizer CLI を実行 |
| `make move-cli SRC=<path> DEST=<path>` | Move CLI を実行 |
| `make dev` | 開発環境構築 + Photo Organizer GUI 起動 |

### 🛠️ 開発用コマンド
| コマンド | 説明 |
|----------|------|
| `make format` | コードを black でフォーマット |
| `make list-packages` | インストール済みパッケージの一覧 |
| `make update-packages` | 依存パッケージのアップデート |
| `make freeze` | requirements.txt の生成 |

### 🧹 クリーンアップ
| コマンド | 説明 |
|----------|------|
| `make clean` | 一時ファイルの削除 |
| `make clean-all` | 仮想環境を含む全ての一時ファイルの削除 |

### 📊 情報表示
| コマンド | 説明 |
|----------|------|
| `make help` | 利用可能なコマンド一覧 |
| `make info` | 環境情報の表示 |

## 🔧 各ツールの詳細

### Photo Organizer

RAW と JPG ファイルの対応関係を管理し、以下の処理を行います：

- **RAW ファイルに対応する JPG ファイルの同期**
- **孤立した RAW/JPG ファイルの管理**
- **ファイルの移動・コピー・削除**
- **ドライランモードでの事前確認**

#### 対応ファイル形式
- **RAW**: ARW (Sony)
- **JPG**: JPG, JPEG

#### 出力構造
```
出力先/
├── ARW/          # RAW ファイル
├── JPG/          # JPG ファイル
└── orphans/      # 対応関係のないファイル
```

### Move

ファイルを日付・拡張子ごとに整理します：

#### 対応ファイル形式
- **画像**: JPEG, JPG, PNG, GIF, BMP, HIF, ARW
- **動画**: MOV, MP4, MPG, MTS, LRF, LRV
- **音声**: WAV, MP3
- **ドキュメント**: XML
- **デザイン**: PSD

#### 出力構造
```
出力先/
├── 2024/
│   ├── 01月/
│   │   ├── 2024-01-15/
│   │   │   ├── JPG/
│   │   │   └── ARW/
│   │   └── 2024-01-16/
│   └── 02月/
└── 2025/
```

## 🔄 ワークフロー例

### 1. カメラからの写真整理
```bash
# 1. 開発環境の構築
make setup

# 2. Photo Organizer GUI で RAW/JPG を同期
make run-photo-organizer

# 3. Move GUI で日付ごとに整理
make run-move
```

### 2. CLI でのバッチ処理
```bash
# RAW/JPG の同期処理
make photo-cli SRC=~/Pictures/Camera DIR=~/Pictures/Organized

# 日付ごとの整理
make move-cli SRC=~/Pictures/Organized DEST=~/Pictures/Archive
```

## 📝 ログ機能

両ツールともログ機能を提供しており、処理の詳細を記録できます：

- **処理されたファイルの一覧**
- **エラーの詳細**
- **実行時間の記録**
- **統計情報**

## 🐛 トラブルシューティング

### 仮想環境が作成できない場合
```bash
# Python の確認
python3 --version

# 仮想環境の再作成
make clean-venv
```

### 依存パッケージのエラー
```bash
# パッケージのアップデート
make update-packages

# 依存関係の確認
make list-packages
```

### GUI が起動しない場合
```bash
# 環境情報の確認
make info

# ログファイルの確認（該当する場合）
cat /path/to/logfile.log
```

---

**🎯 Quick Start**: `make dev` で開発環境を構築し、すぐに Photo Organizer GUI を起動できます！