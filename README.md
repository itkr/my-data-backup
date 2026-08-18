# My Data Backup

RAW/JPG ファイルの整理と管理を効率化するツール集

## 概要

デジタルカメラで撮影した RAW/JPG ファイルを整理・管理するための Python ツールです。
GUI と CLI の両方を備え、RAW/JPG の対応付けと、日付・拡張子ごとの自動整理を行います。

## 主な機能

### Photo Organizer

RAW と JPG の対応関係を判定し、種類ごとに振り分けます。

- 同名の RAW/JPG をペアとして認識
- 対応相手のないファイルは `orphans/` に隔離
- 出力先に同名ファイルがある場合はスキップ（既存ファイルを上書きしません）
- ドライランでの事前確認

#### 対応ファイル形式

| 分類 | 拡張子 |
|------|--------|
| RAW | ARW, RAW, CR2, NEF, DNG |
| JPG | JPG, JPEG |

#### 出力構造

```
出力先/
├── ARW/          # RAW ファイル
├── JPG/          # JPG ファイル
└── orphans/      # 対応関係のないファイル
```

### Move

ファイルを撮影日・拡張子ごとのディレクトリに整理します。

- 日付ごとのディレクトリを自動生成
- 移動先に同名ファイルがある場合は連番を付与
- サブディレクトリを含める再帰検索（任意）
- ドライランでの事前確認

#### 対応ファイル形式

対応拡張子は [`src/core/config/file_extensions.py`](src/core/config/file_extensions.py) で一元管理されています。

| 分類 | 拡張子 |
|------|--------|
| RAW | ARW, RAW, CR2, NEF, DNG |
| JPG | JPG, JPEG |
| 動画 | MOV, MP4, MPG, AVI, MTS, LRF, LRV |
| 音声 | WAV, MP3, AAC, FLAC |
| ドキュメント | XML, TXT, PDF, DOC, DOCX |

> **未対応**: PNG, GIF, BMP, HIF, PSD は対象外です。これらのファイルは移動されず、その場に残ります。
>
> 対象拡張子は実行時にも確認できます:
> ```bash
> python src/main.py move get-suffixes
> ```

#### 出力構造

拡張子ディレクトリは常に大文字になります（`.arw` も `.ARW` も `ARW/` にまとまります）。

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

## プロジェクト構造

```
my-data-backup/
├── Makefile              # 開発環境の自動化
├── pyproject.toml        # パッケージ定義
├── requirements.txt      # Python 依存パッケージ
├── src/
│   ├── main.py           # 統一エントリーポイント（Typer）
│   ├── app/              # アプリケーション層
│   │   ├── gui/          # GUI
│   │   │   ├── app.py            # 統合GUIアプリケーション
│   │   │   ├── base/             # タブの基底クラス
│   │   │   └── modules/          # 機能ごとのタブ
│   │   └── cli/          # CLI
│   │       ├── photo_organizer.py
│   │       ├── move.py
│   │       └── display.py        # 進捗・結果表示
│   ├── core/             # ビジネスロジック層
│   │   ├── config/       # 設定・拡張子定義
│   │   ├── domain/       # ドメインモデルとリポジトリ interface
│   │   └── services/     # サービス層
│   ├── infrastructure/   # インフラ層
│   │   ├── repositories.py       # ファイルシステム実装
│   │   └── logging/              # ログ設定
│   └── tests/
├── samples/              # サンプルスクリプト
└── docs/
```

### アーキテクチャ

- **サービス層パターン**: ビジネスロジックとファイル操作を分離
- **リポジトリパターン**: `core/domain/repositories` の interface に対して `infrastructure` が実装を提供
- **依存性注入**: サービスはリポジトリを受け取るため、テストで差し替え可能

## セットアップ

### 前提条件

- Python 3.9 以上
- macOS / Linux
- Git

### 手順

```bash
git clone <repository-url>
cd my-data-backup
make setup
```

`make setup` は仮想環境の作成と、開発可能パッケージとしてのインストールまで行います。

環境の確認:

```bash
make info
make check-env
```

## 使用方法

### 統合GUI

```bash
make run-gui
```

### CLI

```bash
# Photo Organizer
python src/main.py photo organize /path/to/source /path/to/output --dry-run

# Move
python src/main.py move organize /path/to/source /path/to/dest --dry-run

# ヘルプ
python src/main.py --help
python src/main.py photo organize --help
python src/main.py move organize --help
```

`make setup` 後は `my-data-backup` コマンドでも同じように実行できます。

```bash
my-data-backup move organize /path/to/source /path/to/dest --dry-run
```

#### 主なオプション

| オプション | 説明 |
|-----------|------|
| `--dry-run` | 実際のファイル操作を行わず、結果だけを確認する |
| `--copy` | 移動ではなくコピーする（原本を残す） |
| `--recursive` | サブディレクトリも検索する（Move のみ） |
| `--suffix` | 対象拡張子を指定する（Move のみ、複数指定可） |

### Makefile 経由での実行

```bash
make run-photo-cli SRC=~/Pictures/Camera DIR=~/Pictures/Organized DRY_RUN=1
make run-move-cli SRC=~/Downloads DEST=~/Documents/Organized DRY_RUN=1
```

### サンプルスクリプト

```bash
./samples/gui.sh               # 統合GUI を起動
./samples/photo_organizer.sh   # Photo Organizer をドライランで実行
./samples/move.sh              # スクリプトが置かれたディレクトリを整理
```

`samples/move.sh` は**スクリプト自身が置かれたディレクトリ**を整理します。
シンボリックリンクを整理したいディレクトリに置いて実行する使い方を想定しています。

## Makefile コマンド一覧

### 環境構築

| コマンド | 説明 |
|----------|------|
| `make setup` | 開発環境の初期セットアップ |
| `make venv` | 仮想環境の作成 |
| `make install` | 依存パッケージのインストール |
| `make reinstall` | 開発可能パッケージの再インストール |
| `make clean-venv` | 仮想環境の再作成 |

### アプリケーション実行

| コマンド | 説明 |
|----------|------|
| `make run-gui` | 統合GUIアプリケーションを起動 |
| `make run-photo-cli SRC=<path> DIR=<path>` | Photo Organizer CLI を実行 |
| `make run-move-cli SRC=<path> DEST=<path>` | Move CLI を実行 |
| `make dev` | 環境構築 + 統合GUI 起動 |

### 開発・品質

| コマンド | 説明 |
|----------|------|
| `make test` | 全てのテストを実行 |
| `make format` | autoflake → isort → black でフォーマット |
| `make lint` | flake8 でコード品質をチェック |
| `make check-env` | 実行環境をチェック |
| `make check-package` | パッケージの状態をチェック |

### 依存パッケージ管理

| コマンド | 説明 |
|----------|------|
| `make list-packages` | インストール済みパッケージの一覧 |
| `make update-packages` | 依存パッケージのアップデート |
| `make freeze` | 現在の環境から requirements を生成 |

### Docker

| コマンド | 説明 |
|----------|------|
| `make docker-build-image` | Dockerイメージをビルド |
| `make docker-run-photo-organizer` | Photo Organizer CLI をDockerで実行 |
| `make docker-run-move` | Move CLI をDockerで実行 |
| `make docker-run-app-gui` | 統合GUI をDockerで起動（X11必要） |
| `make docker-shell` | Dockerコンテナのシェルにアクセス |
| `make docker-status` | Docker環境の状態確認 |
| `make docker-help` | Docker専用ヘルプを表示 |

詳細は [docs/DOCKER.md](docs/DOCKER.md) を参照してください。

### クリーンアップ

| コマンド | 説明 |
|----------|------|
| `make clean` | 一時ファイルの削除 |
| `make clean-all` | 仮想環境を含む全ての一時ファイルの削除 |

## ワークフロー例

```bash
# 1. 環境構築
make setup

# 2. まずドライランで結果を確認
python src/main.py photo organize ~/Pictures/Camera ~/Pictures/Organized --dry-run

# 3. 問題なければ実行
python src/main.py photo organize ~/Pictures/Camera ~/Pictures/Organized

# 4. 日付ごとに整理
python src/main.py move organize ~/Pictures/Organized ~/Pictures/Archive
```

GUI で操作する場合は `make run-gui` から同じ処理を実行できます。

## ログ

処理内容は標準出力に記録されます。

- スキャン結果とフィルタリング結果
- 各ファイルの移動・コピー・スキップ
- エラーの詳細
- 成功・スキップ・失敗の集計

ドライラン時は `[DRY RUN]` 付きで、実行された場合の移動先が出力されます。

## トラブルシューティング

### 仮想環境が作成できない

```bash
python3 --version
make clean-venv
```

### 依存パッケージのエラー

```bash
make update-packages
make list-packages
```

### GUI が起動しない

```bash
make check-env
```

`tkinter` が利用不可の場合は、macOS では `brew install python-tk`、
Ubuntu では `sudo apt-get install python3-tk` が必要です。

---

**Quick Start**: `make setup && make run-gui`
