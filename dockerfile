# ベースイメージを指定
FROM python:3.11-slim

# 環境変数を設定
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# システムパッケージを更新し、mysqlclientのビルドに必要なライブラリをすべてインストール
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリを作成して設定
WORKDIR /app

# 必要なパッケージをインストール
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# プロジェクトファイルをコピー
COPY . /app/