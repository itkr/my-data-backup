# Python公式イメージをベースとして使用
FROM python:3.11-slim

# メンテナーの情報
LABEL maintainer="itkr"
LABEL description="Photo Organizer and File Move Tools with GUI"

# 作業ディレクトリを設定
WORKDIR /app

# システムパッケージの更新とGUI関連ライブラリのインストール
# tkinter、customtkinter、opencv用の依存関係を含む
RUN apt-get update && apt-get install -y \
    # GUI関連
    python3-tk \
    x11-apps \
    xvfb \
    # OpenCV用の依存関係
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgtk-3-0 \
    # その他の必要なパッケージ
    curl \
    make \
    && rm -rf /var/lib/apt/lists/*

# Pythonの依存関係をコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# プロジェクトファイルをコピー
COPY . .

# 環境変数を設定
ENV PYTHONPATH=/app
ENV DISPLAY=:0

# ボリュームマウントポイントを作成
VOLUME ["/data"]

# GUIアプリケーション用のユーザーを作成（セキュリティ向上）
RUN useradd -m -s /bin/bash appuser && \
    chown -R appuser:appuser /app

# 非rootユーザーに切り替え
USER appuser

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; import customtkinter; import cv2; print('Dependencies OK')" || exit 1

# デフォルトコマンド（v2.0新アーキテクチャ対応）
CMD ["python", "-c", "print('🐳 Docker Container Ready! (v2.0)\\n\\n📋 v2.0 統合アプリケーション:\\n  cd src && python main.py --help        # 統合CLI ヘルプ\\n  cd src && python main.py gui            # 統合GUI (requires X11)\\n  cd src && python main.py cli photo --help # Photo Organizer CLI\\n  cd src && python main.py cli move --help  # Move CLI\\n\\n🏛️ レガシー版コマンド:\\n  make run-photo-organizer   # Photo Organizer CLI\\n  make run-move              # Move CLI\\n  make run-photo-organizer-gui # Photo Organizer GUI (requires X11)\\n  make run-move-gui          # Move GUI (requires X11)\\n\\n📁 Mount your data to /data volume')"]

# メタデータ
LABEL version="2.0"
LABEL architecture="modular-component"
LABEL org.opencontainers.image.source="https://github.com/itkr/my-data-backup"
