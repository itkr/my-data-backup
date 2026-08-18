# Docker 使用ガイド

このガイドでは、my-data-backupツールをDockerで使用する方法を詳しく説明します。Dockerを使用することで、ローカル環境にPythonや依存関係をインストールすることなく、すぐにツールを利用できます。

## Docker使用のメリット

- **環境構築不要**: Python環境の構築やパッケージインストールが不要
- **一貫性**: どの環境でも同じ動作を保証
- **隔離性**: ホストシステムに影響を与えない
- **簡単な削除**: 不要になったら簡単にクリーンアップ可能

## 必要な環境

- **Docker**: 20.10 以上
- **Docker Compose**: 2.0 以上（オプション）
- **GUI使用時**: 
  - **macOS**: XQuartz
  - **Linux**: X11サーバー

## クイックスタート

### 1. リポジトリのクローン

```bash
git clone https://github.com/itkr/my-data-backup.git
cd my-data-backup
```

### 2. Dockerイメージのビルド

```bash
# Makefile を使用（推奨）
make docker-build-image

# または Docker Compose を使用
docker-compose build

# または手動ビルド
docker build -t my-data-backup:latest .
```

### 3. すぐに使用開始

#### Move CLI でファイル整理
```bash
# CLIコンテナを起動
make docker-run-cli

# ファイル整理を実行（テスト用）
make docker-run-move
```

#### Photo Organizer でRAW/JPG同期
```bash
# Photo Organizer を実行
make docker-run-photo-organizer
```

### 3. コンテナの起動

#### CLIモードの場合

```bash
# CLIコンテナを起動
docker-compose up -d my-data-backup-cli

# コンテナに入る
docker exec -it my-data-backup-cli bash

# ツールを実行
make run-photo-organizer-gui  # Photo Organizer GUI
make run-move-gui             # Move GUI
```

#### GUIモードの場合

```bash
# GUIセットアップスクリプトを実行
./docker-gui.sh

# または手動でGUIコンテナを起動
docker-compose up -d my-data-backup-gui
```

## データのマウント

### ディレクトリ構造

```bash
my-data-backup/
├── data/              # ← ここにファイルを配置
│   ├── ARW/          # RAWファイル
│   ├── JPG/          # JPGファイル
│   └── import/       # 整理対象ファイル
├── logs/             # ログファイル（永続化）
└── export/           # 出力先（自動作成）
```

### ファイルの配置

```bash
# ローカルのファイルをdataディレクトリにコピー
cp -r /path/to/your/photos/* ./data/

# または直接マウント（docker-compose.yml を編集）
volumes:
  - /your/photo/directory:/data
```

## GUI アプリケーションの使用

### macOS での GUI 使用

1. **XQuartz のインストール**
```bash
brew install --cask xquartz
# または https://www.xquartz.org/ からダウンロード
```

2. **XQuartz の設定**
```bash
# XQuartz を起動
open -a XQuartz

# 設定 > セキュリティ で以下をチェック:
# ☑ "ネットワーククライアントからの接続を許可"
```

3. **GUI アプリケーションの起動**
```bash
# 自動セットアップ
./docker-gui.sh

# 手動起動
export DISPLAY=host.docker.internal:0
xhost +localhost
docker exec -it my-data-backup-gui python photo_organizer/gui.py
```

### Linux での GUI 使用

```bash
# X11フォワーディングを許可
xhost +local:docker

# GUIアプリケーションを起動
docker exec -it my-data-backup-gui python photo_organizer/gui.py
```

## 利用可能なコマンド

### Makefileコマンド（統一インターフェース）

```bash
# 新しい統一コマンド（推奨）
# Photo Organizer CLI をDockerで実行
make docker-run-photo-organizer

# Move CLI をDockerで実行
make docker-run-move

# Photo Organizer GUI をDockerで実行
make docker-run-photo-organizer-gui

# Move GUI をDockerで実行
make docker-run-move-gui

# Docker専用ヘルプを表示
make docker-help
```

### Makefile.docker直接実行

```bash
# CLIモードでコンテナを起動
make -f Makefile.docker docker-run

# GUIモードの設定と起動
make -f Makefile.docker docker-gui

# Photo Organizer CLI
make -f Makefile.docker docker-photo-organizer

# Move CLI
make -f Makefile.docker docker-move

# Photo Organizer GUI
make -f Makefile.docker docker-photo-organizer-gui

# Move GUI
make -f Makefile.docker docker-move-gui

# コンテナシェルにアクセス
make -f Makefile.docker docker-shell

# ログ表示
make -f Makefile.docker docker-logs

# クリーンアップ
make -f Makefile.docker docker-clean

# 完全クリーンアップ
make -f Makefile.docker docker-clean-all

# 状態確認
make -f Makefile.docker docker-status
```

### 直接Dockerコマンド

```bash
# Photo Organizer CLI
docker exec -it my-data-backup-cli python photo_organizer/main.py --help

# Move CLI  
docker exec -it my-data-backup-cli python move/main.py --help

# Photo Organizer GUI
docker exec -it my-data-backup-gui python photo_organizer/gui.py

# Move GUI
docker exec -it my-data-backup-gui python move/gui.py
```

## カスタマイズ

### 環境変数

```bash
# docker-compose.yml または .env ファイルで設定
PYTHONPATH=/app
DISPLAY=:0  # Linux用
DISPLAY=host.docker.internal:0  # macOS用
```

### ボリュームマウント

```yaml
# docker-compose.yml でカスタマイズ
volumes:
  - ./data:/data                    # データディレクトリ
  - ./logs:/app/logs               # ログディレクトリ  
  - /your/path:/custom/path        # カスタムパス
```

## トラブルシューティング

### GUI が表示されない

**macOS:**
```bash
# XQuartz が起動しているか確認
ps aux | grep -i xquartz

# DISPLAY 環境変数を確認
echo $DISPLAY

# XQuartz の設定を確認
xhost +localhost
```

**Linux:**
```bash
# X11フォワーディングを確認
echo $DISPLAY
xhost +local:docker

# Xサーバーが起動しているか確認
ps aux | grep -i xorg
```

### コンテナが起動しない

```bash
# ログを確認
docker-compose logs my-data-backup-cli
docker-compose logs my-data-backup-gui

# コンテナの状態を確認
docker ps -a

# イメージを再ビルド
docker-compose build --no-cache
```

### 権限エラー

```bash
# データディレクトリの権限を確認
ls -la data/

# 権限を修正
chmod -R 755 data/
```

## アップデート

```bash
# 最新のコードを取得
git pull origin main

# イメージを再ビルド
docker-compose build --no-cache

# 古いコンテナを削除
docker-compose down
docker-compose up -d
```

## パフォーマンス最適化

### マルチステージビルド（高度な用途）

```dockerfile
# Dockerfile.optimized
FROM python:3.11-slim as builder
RUN pip install --user -r requirements.txt

FROM python:3.11-slim
COPY --from=builder /root/.local /root/.local
# ... 残りの設定
```

### リソース制限

```yaml
# docker-compose.yml
services:
  my-data-backup-cli:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          memory: 512M
```

## 🆘 サポート

問題が発生した場合:

1. **ログの確認**: `docker-compose logs`
2. **環境の確認**: `make -f Makefile.docker docker-status`  
3. **イシューの報告**: [GitHub Issues](https://github.com/itkr/my-data-backup/issues)

---

 このドキュメントに関する質問や改善提案があれば、お気軽にお知らせください。
