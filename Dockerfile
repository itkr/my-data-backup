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
CMD ["python", "-c", "print('Docker Container Ready\\n\\nコマンド:\\n  python src/main.py --help                 # ヘルプ\\n  python src/main.py gui                    # 統合GUI (requires X11)\\n  python src/main.py photo organize --help  # Photo Organizer CLI\\n  python src/main.py move organize --help   # Move CLI\\n\\nデータは /data ボリュームにマウントしてください')"]

# メタデータ
LABEL version="2.0"
LABEL architecture="modular-component"
LABEL org.opencontainers.image.source="https://github.com/itkr/my-data-backup"
