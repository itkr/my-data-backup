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

### 🏗️ v2.0 新アーキテクチャ（推奨）

```
my-data-backup/
├── Makefile              # 開発環境の自動化
├── README.md             # このファイル
├── requirements.txt      # Python 依存パッケージ
├── venv/                 # Python 仮想環境
├── src/                  # 新アーキテクチャ（v2.0）
│   ├── main.py          # 統一エントリーポイント
│   ├── app/             # アプリケーション層
│   │   ├── gui/         # GUI層
│   │   │   └── app.py   # 統合GUIアプリケーション（メイン）
│   │   └── cli/         # CLI層
│   │       ├── photo_organizer.py # Photo Organizer CLI (v2.0)
│   │       └── move.py          # Move CLI (v2.0)
│   ├── core/            # ビジネスロジック層
│   │   ├── domain/      # ドメイン層
│   │   │   └── models.py      # データモデル
│   │   └── services.py         # サービス層（ビジネスロジック）
│   └── infrastructure/  # インフラ層
│       ├── repositories.py    # ファイルシステム実装
│       └── logging.py         # 統一ログシステム
├── common/               # 共通ライブラリ（レガシー）
│   ├── __init__.py      # 初期化ファイル
│   └── logger.py        # 統一ログ機構
├── photo_organizer/      # Photo Organizer ツール（レガシー）
```

### 🏛️ アーキテクチャの特徴

**v2.0 新アーキテクチャ**は、以下の設計原則に基づいて構築されています：

- **🏗️ モジュラー・コンポーネント構造**: 責任の分離と高い再利用性
- **🔄 サービス層パターン**: ビジネスロジックとインフラの分離
- **🧪 テスタビリティ**: 依存性注入による高いテスト容易性
- **🎨 統合インターフェース**: GUI/CLI の統一されたユーザー体験
- **📊 統一ログシステム**: 全コンポーネントで共通のログ機構

### 📁 レガシー構造（v1.0）

```
├── photo_organizer/      # Photo Organizer ツール（レガシー）
│   ├── main.py          # CLI インターフェース
│   └── gui.py           # GUI インターフェース
└── move/                 # Move ツール（レガシー）
    ├── main.py          # CLI インターフェース
    └── gui.py           # GUI インターフェース
```

## クイックスタート

### 🐳 Docker使用（推奨）- 環境構築不要
```bash
# 1. リポジトリのクローン
git clone <repository-url>
cd my-data-backup

# 2. Dockerイメージをビルド
make docker-build-image

# 3. すぐに使用開始
# ファイル整理の例
make docker-run-move
# または Photo Organizer を使用
make docker-run-photo-organizer
```

### 💻 ローカル環境での使用（v2.0推奨）
```bash
# 1. 開発環境の構築
make setup

# 2. 統合GUIアプリケーション を起動（v2.0）
make run-gui

# 3. 新アーキテクチャ版CLI（推奨）
cd src && python main.py --help
```

### 💻 レガシー版の使用
```bash
# レガシー版Photo Organizer GUI
make run-photo-organizer-gui

# レガシー版Move GUI
make run-move-gui
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

### 4. Docker での使用（推奨）
```bash
# Dockerイメージをビルド
make docker-build-image

# CLIコンテナを起動
make docker-run-cli

# アプリケーションを実行
make docker-run-move
make docker-run-photo-organizer

# GUIモードで起動（macOS/Linux、X11フォワーディング必要）
make docker-run-move-gui
make docker-run-photo-organizer-gui
```

詳細なDocker使用方法は [DOCKER.md](DOCKER.md) を参照してください。

## 🎮 使用方法

### 🚀 v2.0 新アーキテクチャ（推奨）

#### 統合GUI
```bash
# 統合GUIアプリケーション（推奨）
make run-gui
# または
cd src && python main.py gui
```

#### 新アーキテクチャ版CLI
```bash
# Photo Organizer CLI (v2.0)
cd src && python main.py cli photo --src /path/to/source --dir /path/to/output --dry-run

# Move CLI (v2.0)
cd src && python main.py cli move --import-dir /path/to/import --export-dir /path/to/export --dry-run

# ヘルプ表示
cd src && python main.py --help
cd src && python main.py cli photo --help
cd src && python main.py cli move --help
```

### 🏛️ レガシー版 (v1.0)

#### GUI での使用

#### Photo Organizer GUI
```bash
make run-photo-organizer-gui
```

#### Move GUI
```bash
make run-move-gui
```

#### CLI での使用

#### Photo Organizer CLI
```bash
# 基本的な使用方法
make run-photo-organizer SRC=/path/to/source DIR=/path/to/output

# 実際の例
make run-photo-organizer SRC=~/Pictures/Camera DIR=~/Pictures/Organized
```

#### Move CLI
```bash
# 基本的な使用方法
make run-move SRC=/path/to/source DEST=/path/to/destination

# 実際の例
make run-move SRC=~/Downloads DEST=~/Documents/Organized
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
| `make run-gui` | **統合GUIアプリケーション を起動（v2.0推奨）** |
| `make run-unified-gui` | **統合GUIアプリケーション を起動（エイリアス）** |
| `make run-unified-app` | **統合アプリケーション（フル版）を起動（v2.0）** |
| `make run-photo-cli-v2` | **Photo Organizer CLI (v2.0) を実行** |
| `make run-move-cli-v2` | **Move CLI (v2.0) を実行** |
| `make run-photo-organizer-gui` | Photo Organizer GUI を起動（レガシー） |
| `make run-move-gui` | Move GUI を起動（レガシー） |
| `make run-photo-organizer SRC=<path> DIR=<path>` | Photo Organizer CLI を実行（レガシー） |
| `make run-move SRC=<path> DEST=<path>` | Move CLI を実行（レガシー） |
| `make dev` | 開発環境構築 + Photo Organizer GUI 起動 |

### 🐳 Docker でのアプリケーション実行
| コマンド | 説明 |
|----------|------|
| `make docker-build-image` | Dockerイメージをビルド |
| **v2.0 新アーキテクチャ** | |
| `make docker-run-v2` | **v2.0統合アプリケーションコンテナを起動** |
| `make docker-run-gui-v2` | **v2.0統合GUIアプリケーションコンテナを起動** |
| `make docker-test-v2` | **v2.0新アーキテクチャのテストを実行** |
| **レガシー版（互換性維持）** | |
| `make docker-run-cli` | CLIコンテナを起動（レガシー） |
| `make docker-run-photo-organizer-gui` | Photo Organizer GUI をDockerで起動 |
| `make docker-run-move-gui` | Move GUI をDockerで起動 |
| `make docker-run-photo-organizer` | Photo Organizer CLI をDockerで実行 |
| `make docker-run-move` | Move CLI をDockerで実行 |
| `make docker-shell` | Dockerコンテナのシェルにアクセス |
| `make docker-logs` | Dockerコンテナのログを表示 |
| `make docker-status` | Docker環境の状態確認 |
| `make docker-clean-docker` | Dockerコンテナ・イメージをクリーンアップ |
| `make docker-help` | Docker専用ヘルプを表示 |

### ️ 開発用コマンド
| コマンド | 説明 |
|----------|------|
| `make format` | コードを black でフォーマット |
| `make test-logger` | 共通ログ機構のテスト実行 |
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

### v2.0 新アーキテクチャでの写真整理（推奨）
```bash
# 1. 開発環境の構築
make setup

# 2. 統合GUIで直感的に操作
make run-gui

# または、CLIでバッチ処理
cd src && python main.py cli photo --src ~/Pictures/Camera --dir ~/Pictures/Organized --dry-run
cd src && python main.py cli move --import-dir ~/Pictures/Organized --export-dir ~/Pictures/Archive --dry-run
```

### 🐳 Docker を使用したカメラからの写真整理
```bash
# 1. Dockerイメージをビルド
make docker-build-image

# 2. Photo Organizer GUI で RAW/JPG を同期（X11フォワーディング必要）
make docker-run-photo-organizer-gui

# 3. Move CLI で日付ごとに整理（テスト用ファイルで確認）
make docker-run-move
```

### 🐳 Docker CLI でのバッチ処理
```bash
# CLIコンテナを起動
make docker-run-cli

# コンテナ内でシェルにアクセス
make docker-shell

# コンテナ内で実行
# RAW/JPG の同期処理
python -m photo_organizer.main --src /data/source --dir /data/output --dry-run

# 日付ごとの整理
python -m move.main --import-dir /data/source --export-dir /data/organized --dry-run
```

### 1. カメラからの写真整理（ローカル環境・レガシー版）
```bash
# 1. 開発環境の構築
make setup

# 2. Photo Organizer GUI で RAW/JPG を同期
make run-photo-organizer-gui

# 3. Move GUI で日付ごとに整理
make run-move-gui
```

### 2. CLI でのバッチ処理（レガシー版）
```bash
# RAW/JPG の同期処理
make run-photo-organizer SRC=~/Pictures/Camera DIR=~/Pictures/Organized

# 日付ごとの整理
make run-move SRC=~/Pictures/Organized DEST=~/Pictures/Archive
```

## 📝 ログ機能

### 🔧 v2.0 統一ログシステムの特徴
- **🏗️ アーキテクチャレベルでの統合**: サービス層、インフラ層で統一されたログ出力
- **📊 構造化ログ**: JSON形式での詳細な処理情報記録
- **🎯 レベル別出力**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **⚡ リアルタイム処理**: 進捗状況のリアルタイム表示
- **🔄 GUI/CLI統合**: 統一されたログ表示インターフェース

### 🏛️ レガシー統一ログ機構の特徴
プロジェクト全体で統一されたログ機構を提供しており、処理の詳細を記録できます：

- **統一されたインターフェース**: 全ツールで同じログ機能を使用
- **柔軟な出力先**: コンソール、ファイル、または両方に出力可能
- **豊富なログレベル**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **特殊メソッド**: success(), progress(), start_operation(), end_operation()
- **後方互換性**: 既存のSyncLoggerとの互換性を維持

### 📊 ログ出力内容
- **処理されたファイルの一覧**
- **エラーの詳細**
- **実行時間の記録**
- **統計情報**
- **操作の開始・終了**

### 🧪 テスト方法
```bash
# 共通ログ機構のテスト
make test-logger
```

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

**🎯 Quick Start v2.0**: `make run-gui` で統合GUIアプリケーション（推奨版）をすぐに起動できます！

**🏛️ Legacy Support**: `make dev` でレガシー版の開発環境を構築し、Photo Organizer GUI を起動できます。