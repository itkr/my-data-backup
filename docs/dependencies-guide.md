## My Data Backup プロジェクトでの依存関係管理

### 📦 pyproject.toml dependencies（パッケージの核となる依存関係）
- **目的**: パッケージが動作するために絶対に必要なもの
- **対象**: エンドユーザーがパッケージをインストールしたときに自動でインストールされる
- **特徴**: バージョン範囲指定で柔軟性を保つ

```toml
dependencies = [
    "customtkinter>=5.2.0",  # GUI機能に必須
    "click>=8.0.0",          # CLI機能に必須  
    "opencv-python>=4.8.0",  # 画像処理に必須
    "Pillow>=9.0.0",         # 画像処理に必須
]
```

### 📋 requirements.txt（環境固定用）
- **目的**: 開発・本番環境で同一バージョンを保証
- **対象**: デプロイ時・CI/CD・環境構築時
- **特徴**: 具体的なバージョンで環境を固定

```
customtkinter==5.2.1  # 開発で確認済みの安定版
click==8.1.7          # 同上
opencv-python==4.10.0.84  # 同上
```

### 🛠️ pyproject.toml optional-dependencies（開発用）
- **目的**: 開発時のみ必要なツール
- **対象**: コード品質管理、テスト、ビルド
- **特徴**: pip install -e ".[dev]" で開発者のみインストール

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",     # テスト
    "black>=22.0.0",     # フォーマッター
    "flake8>=4.0.0",     # リンター
    "autopep8>=2.0.0",   # 自動修正
    "autoflake>=2.0.0",  # 未使用インポート削除
    "isort>=5.0.0",      # インポート整理
]
```
