# RAW/JPG ファイル整理ツール開発用 Makefile
# venv を使った Python 仮想環境での開発環境構築・管理を自動化

# 設定
VENV_DIR = venv
PYTHON = $(shell pwd)/$(VENV_DIR)/bin/python
PIP = $(shell pwd)/$(VENV_DIR)/bin/pip
REQUIREMENTS = requirements.txt

# デフォルトターゲット
.DEFAULT_GOAL := help

help: ## ヘルプを表示
	@echo "🐍 ローカル開発環境コマンド"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -v "🐳\|📸\|📁\|🎨\|📊\|📋\|🐚\|🧹\|🏗️\|🔍\|📦\|🚀\|✨\|🧪\|🏚️" | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "🧪 テスト・検証"
	@grep -E '^[a-zA-Z_-]+:.*?## .*🧪.*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "🏗️ 開発環境構築・管理"
	@grep -E '^[a-zA-Z_-]+:.*?## .*🏗️.*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "🔍 開発ツール・ユーティリティ"
	@grep -E '^[a-zA-Z_-]+:.*?## .*🔍.*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "📦 依存パッケージ管理"
	@grep -E '^[a-zA-Z_-]+:.*?## .*📦.*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "🚀 アプリケーション実行"
	@grep -E '^[a-zA-Z_-]+:.*?## .*🚀.*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "✨ クリーンアップ"
	@grep -E '^[a-zA-Z_-]+:.*?## .*✨.*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "🐳 Docker環境コマンド"
	@grep -E '^[a-zA-Z_-]+:.*?## .*🐳.*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[34m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "📱 Docker アプリケーション実行"
	@grep -E '^[a-zA-Z_-]+:.*?## .*(📸|📁|🎨).*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[34m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "🔧 Docker 管理・監視"
	@grep -E '^[a-zA-Z_-]+:.*?## .*(📊|📋|🐚|🧹).*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[34m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "🏚️ レガシーコマンド（互換性維持）"
	@grep -E '^[a-zA-Z_-]+:.*?## .*🏚️.*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[35m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "💡 詳細なDockerヘルプ: make docker-help"
	@echo ""
	@echo "📖 ドキュメント"
	@echo "  開発パッケージの注意点: docs/development-package.md"

# 仮想環境構築
.PHONY: venv
venv: ## 🏗️ 仮想環境を作成（既に存在する場合はスキップ）
	@if [ -d "$(VENV_DIR)" ]; then \
		echo "仮想環境 '$(VENV_DIR)'"; \
	else \
		echo "仮想環境 '$(VENV_DIR)' を作成中..."; \
		python3 -m venv $(VENV_DIR); \
		echo "仮想環境を作成しました"; \
	fi

# 依存パッケージのインストール
.PHONY: install
install: venv ## 🏗️ 依存パッケージをインストール
	@echo "依存パッケージをインストール中..."
	$(PIP) install --upgrade pip
	# 本番用依存関係
	$(PIP) install -r $(REQUIREMENTS)
	@echo "開発可能パッケージとしてインストール中..."
	# 開発用依存関係を含めてインストール
	$(PIP) install -e ".[dev]"
	@echo "依存パッケージのインストールが完了しました"

# 開発用セットアップ（初回実行時）
.PHONY: setup
setup: venv install ## 🏗️ 開発環境を初期セットアップ
	@echo "開発環境のセットアップが完了しました"
	@echo "以下のコマンドで各ツールを実行できます:"
	@echo "  make run-gui             # 統合GUIアプリケーション"
	@echo "  make run-photo-cli       # Photo Organizer CLI"
	@echo "  make run-move-cli        # Move CLI"

# 統合GUI を実行
.PHONY: run-gui
run-gui: venv check-env ## 🚀 統合GUIアプリケーション を実行
	@echo "統合GUIアプリケーション を起動中..."
	cd src && PYTHONPATH=$(shell pwd) $(PYTHON) -m app.gui.app

# Photo Organizer CLI を実行
.PHONY: run-photo-cli
run-photo-cli: venv check-env ## 🚀 Photo Organizer CLI を実行（引数: SRC=ソース DIR=出力先）
	@if [ -z "$(SRC)" ] || [ -z "$(DIR)" ]; then \
		echo "使用方法: make run-photo-cli SRC=<ソース> DIR=<出力先> [DRY_RUN=1]"; \
		exit 1; \
	fi
	$(PYTHON) src/main.py photo organize "$(SRC)" "$(DIR)" $(if $(DRY_RUN),--dry-run)

# Move CLI を実行
.PHONY: run-move-cli
run-move-cli: venv check-env ## 🚀 Move CLI を実行（引数: SRC=ソース DEST=出力先）
	@if [ -z "$(SRC)" ] || [ -z "$(DEST)" ]; then \
		echo "使用方法: make run-move-cli SRC=<ソース> DEST=<出力先> [DRY_RUN=1]"; \
		exit 1; \
	fi
	$(PYTHON) src/main.py move organize "$(SRC)" "$(DEST)" $(if $(DRY_RUN),--dry-run)

# テスト実行
.PHONY: test
test: venv ## 🧪 全てのテストを実行
	$(PYTHON) -m pytest src/tests

# ========================================
# Code Quality & Formatting Commands
# ========================================

# 統一されたコードフォーマット（推奨順序）
.PHONY: format
format: venv ## 🔍 統一されたコードフォーマット（autoflake→isort→black）
	@echo "🧹 統一されたコードフォーマットを実行中..."
	@echo "1️⃣ 未使用importを削除中 (autoflake)..."
	$(PYTHON) -m autoflake --in-place --remove-all-unused-imports --remove-unused-variables --recursive src/
	@echo "2️⃣ importを整理中 (isort)..."
	$(PYTHON) -m isort src/
	@echo "3️⃣ コード全体をフォーマット中 (black)..."
	$(PYTHON) -m black src/
	@echo "✅ 統一フォーマットが完了しました"
	@echo "🔍 結果を確認中..."
	@if $(PYTHON) -m flake8 src/ --statistics; then \
		echo "✅ コード品質チェック: エラーなし"; \
	else \
		echo "⚠️ まだいくつかのエラーが残っています"; \
	fi

# コード品質チェック
.PHONY: lint
lint: venv ## 🔍 flake8 でコード品質をチェック
	@echo "コード品質をチェック中..."
	$(PYTHON) -m flake8 src/ --statistics
	@echo "コード品質チェックが完了しました"

# 依存パッケージのバージョン確認
.PHONY: list-packages
list-packages: venv ## 📦 インストール済みパッケージの一覧表示
	@echo "インストール済みパッケージ:"
	$(PIP) list

# パッケージ状態チェック
.PHONY: check-package
check-package: venv ## 🔍 開発可能パッケージの状態をチェック
	@echo "パッケージ状態をチェック中..."
	@./scripts/check_package.sh

# パッケージ再インストール
.PHONY: reinstall
reinstall: venv ## 🏗️ 開発可能パッケージを再インストール
	@echo "パッケージを再インストール中..."
	$(PIP) uninstall -y my-data-backup || true
	$(PIP) install -e ".[dev]"
	@echo "再インストールが完了しました"

# 依存パッケージのアップデート
.PHONY: update-packages
update-packages: venv ## 📦 依存パッケージをアップデート
	@echo "依存パッケージをアップデート中..."
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade -r $(REQUIREMENTS)
	@echo "アップデートが完了しました"

# requirements.txt の生成（現在のパッケージから）
.PHONY: freeze
freeze: venv ## 📦 現在の環境から requirements.txt を生成
	@echo "requirements.txt を生成中..."
	$(PIP) freeze > requirements-freeze.txt
	@echo "requirements-freeze.txt に出力しました"

# 開発用情報表示
.PHONY: info
info: ## 🔍 環境情報を表示
	@echo "=== 開発環境情報 ==="
	@echo "Python バージョン: $(shell $(PYTHON) --version 2>/dev/null || echo '仮想環境が未作成')"
	@echo "仮想環境パス: $(VENV_DIR)"
	@echo "Requirements ファイル: $(REQUIREMENTS)"
	@echo "利用可能なツール:"
	@echo "  - Photo Organizer (make run-photo-cli)"
	@echo "  - Move (make run-move-cli)"
	@echo ""

# 環境チェック
.PHONY: check-env
check-env: venv ## 🔍 実行環境をチェック
	@echo "=== 環境チェック ==="
	@echo "Python バージョン: $(shell $(PYTHON) --version)"
	@echo "tkinter チェック中..."
	@$(PYTHON) -c "import tkinter; print('✓ tkinter: 利用可能')" || echo "✗ tkinter: 利用不可 - sudo apt-get install python3-tk (Ubuntu) または brew install python-tk (macOS) が必要"
	@echo "customtkinter チェック中..."
	@$(PYTHON) -c "import customtkinter; print('✓ customtkinter:', customtkinter.__version__)" || echo "✗ customtkinter: 利用不可 - pip install customtkinter が必要"
	@echo "OpenCV チェック中..."
	@$(PYTHON) -c "import cv2; print('✓ OpenCV:', cv2.__version__)" || echo "✗ OpenCV: 利用不可"
	@echo "ディスプレイ環境チェック中..."
	@if [ -z "$$DISPLAY" ] && [ "$$(uname)" != "Darwin" ]; then \
		echo "✗ DISPLAY: X11ディスプレイが設定されていません"; \
		echo "  リモート環境の場合: ssh -X または ssh -Y でログイン"; \
		echo "  WSLの場合: X11サーバー (VcXsrv等) が必要"; \
	else \
		echo "✓ DISPLAY: 設定済み"; \
	fi
	@echo ""

# クリーンアップ
.PHONY: clean
clean: ## ✨ 一時ファイルを削除
	@echo "一時ファイルを削除中..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".DS_Store" -delete
	find . -type f -name "*_old.py" -exec rm -f {} + 2>/dev/null || true
	@echo "クリーンアップが完了しました"

# 仮想環境を削除して再作成
.PHONY: clean-venv
clean-venv: ## ✨ 仮想環境を削除して再作成
	@echo "仮想環境を削除中..."
	rm -rf $(VENV_DIR)
	@echo "仮想環境を再作成中..."
	python3 -m venv $(VENV_DIR)
	@echo "仮想環境を再作成しました"

# 完全なクリーンアップ（仮想環境も削除）
.PHONY: clean-all
clean-all: clean ## ✨ 仮想環境を含む全ての一時ファイルを削除
	@echo "仮想環境を含む全ての一時ファイルを削除中..."
	rm -rf $(VENV_DIR)
	@echo "完全なクリーンアップが完了しました"

# 開発用のクイックスタート
.PHONY: dev
dev: setup ## 🎯 開発環境を構築して統合GUI を起動
	@echo "開発環境構築後、統合版 GUI を起動します..."
	$(MAKE) run-gui

# ================================
# Docker コマンドエイリアス
# ================================

# Docker環境の管理
.PHONY: docker-help docker-build-image docker-run-cli docker-run-gui docker-quickstart
docker-help: ## 🐳 Dockerコマンドのヘルプを表示
	@$(MAKE) -f Makefile.docker help

docker-build-image: ## 🐳 Dockerイメージをビルド
	@$(MAKE) -f Makefile.docker docker-build

# v2.0 新アーキテクチャ用Dockerコマンド
docker-run-v2: ## 🐳 v2.0統合アプリケーションコンテナを起動
	@echo "🚀 v2.0統合アプリケーションコンテナを起動中..."
	docker-compose run --rm my-data-backup-v2 /bin/bash

docker-run-gui-v2: ## 🐳 v2.0統合GUIアプリケーションコンテナを起動
	@echo "🚀 v2.0統合GUIアプリケーションコンテナを起動中..."
	@echo "⚠️  注意: X11フォワーディングが設定されていることを確認してください"
	docker-compose run --rm my-data-backup-gui-v2 /bin/bash

docker-test-v2: ## 🐳 v2.0新アーキテクチャのテストを実行
	@echo "🧪 v2.0新アーキテクチャのテストを実行中..."
	docker-compose run --rm my-data-backup-v2 python -m pytest src/tests

# レガシー版Dockerコマンド（互換性維持）
docker-run-cli: ## 🏚️ 【レガシー】CLIモードでDockerコンテナを起動
	@$(MAKE) -f Makefile.docker docker-run

docker-run-gui: ## 🏚️ 【レガシー】GUIモードでDockerコンテナを起動
	@$(MAKE) -f Makefile.docker docker-gui

docker-quickstart: ## 🐳 Docker環境のワンクリックセットアップ（ビルド→起動→テスト実行）
	@echo "🚀 Docker環境のクイックスタートを開始します..."
	@echo "📦 1. Dockerイメージをビルド中..."
	@$(MAKE) docker-build-image
	@echo "🐳 2. CLIコンテナを起動中..."
	@$(MAKE) docker-run-cli
	@echo "✅ 3. セットアップ完了！テスト実行を開始..."
	@echo "📁 Move CLI をテスト実行中..."
	@$(MAKE) docker-run-move
	@echo ""
	@echo "🎉 Docker環境のセットアップが完了しました！"
	@echo "💡 以下のコマンドでアプリケーションを使用できます："
	@echo "   make docker-run-move                    # ファイル整理"
	@echo "   make docker-run-photo-organizer         # RAW/JPG同期"
	@echo "   make docker-shell                       # コンテナのシェルにアクセス"
	@echo "   make docker-help                        # Docker専用ヘルプ"

# Dockerでアプリケーション実行
.PHONY: docker-run-photo-organizer docker-run-move docker-run-photo-organizer-gui docker-run-move-gui
docker-run-photo-organizer: ## 📸 Photo Organizer CLI をDockerで実行
	@$(MAKE) -f Makefile.docker docker-photo-organizer

docker-run-move: ## 📁 Move CLI をDockerで実行
	@$(MAKE) -f Makefile.docker docker-move

docker-run-photo-organizer-gui: ## 🎨 Photo Organizer GUI をDockerで実行
	@$(MAKE) -f Makefile.docker docker-photo-organizer-gui

docker-run-move-gui: ## 🎨 Move GUI をDockerで実行
	@$(MAKE) -f Makefile.docker docker-move-gui

# Docker管理
.PHONY: docker-status docker-logs docker-shell docker-clean-docker
docker-status: ## 📊 Docker環境の状態確認
	@$(MAKE) -f Makefile.docker docker-status

docker-logs: ## 📋 Dockerコンテナのログを表示
	@$(MAKE) -f Makefile.docker docker-logs

docker-shell: ## 🐚 Dockerコンテナのシェルにアクセス
	@$(MAKE) -f Makefile.docker docker-shell

docker-clean-docker: ## 🧹 Dockerコンテナ・イメージをクリーンアップ
	@$(MAKE) -f Makefile.docker docker-clean-all
