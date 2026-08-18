# MakefileからMakefile.dockerコマンドを呼び出す方法

このプロジェクトでは、MakefileからMakefile.dockerのコマンドを簡単に呼び出せるようにしています。

## 実装方法

### 方法1: エイリアス方式（採用）

```makefile
# Docker コマンドエイリアス
docker-help: ## [docker] Dockerコマンドのヘルプを表示
	@$(MAKE) -f Makefile.docker help

docker-build-image: ## [docker] Dockerイメージをビルド
	@$(MAKE) -f Makefile.docker docker-build
```

**利点**:
- ターゲット名の重複なし
- 明確な分離
- 個別にカスタマイズ可能

### 方法2: include方式（非採用）

```makefile
# Docker用のMakefileも取り込み
-include Makefile.docker
```

**問題点**:
- ターゲット名が重複して警告が出る
- 予期しない動作の可能性

## 使用例

### 基本コマンド

```bash
# ローカル環境
make help                    # ローカル開発コマンド一覧
make setup                   # 環境構築
make run-gui                 # 統合GUI

# Docker環境（エイリアス経由）
make docker-help             # Dockerコマンド一覧
make docker-build-image      # イメージビルド
make docker-run-photo-organizer  # Photo Organizer CLI
make docker-run-app-gui          # 統合GUI

# Docker環境（直接呼び出し）
make -f Makefile.docker help
make -f Makefile.docker docker-build
```

### 利点

1. **統一されたインターフェース**: 一つのMakefileですべてアクセス可能
2. **分かりやすい命名**: `docker-*` プレフィックスで明確に区別
3. **ヘルプの統合**: カテゴリ分けされた見やすいヘルプ
4. **選択の自由**: エイリアス経由でも直接呼び出しでも可能

## 実際の動作

```bash
# 統合ヘルプ
$ make help
使い方: make <target>

アプリケーション実行
  run-gui                    統合GUIアプリケーション を実行
  ...

Docker
  docker-build-image         Dockerイメージをビルド
  docker-help                Dockerコマンドのヘルプを表示

# Docker詳細ヘルプ
$ make docker-help
Docker コマンド一覧
========================

基本操作:
  make -f Makefile.docker docker-build           Dockerイメージをビルド
  ...

# エイリアス経由での実行
$ make docker-status
Docker Environment Status
============================
```

この仕組みにより、開発者は環境を意識せずに適切なコマンドを選択できます。
