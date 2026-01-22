# ベースとなるPythonの環境を指定
FROM python:3.11-slim

# 環境変数を設定
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# コンテナ内の作業場所を作成
WORKDIR /app

# 必要なライブラリをインストール
COPY requirements.txt /app/

# mysqlclientのビルドに必要なツールをインストール
RUN apt-get update && apt-get install -y build-essential default-libmysqlclient-dev pkg-config

# pipをアップグレードし、requirements.txtからライブラリをインストール
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# プロジェクトファイルを全部コピー
COPY . /app/

# コンテナが8000番ポートで通信することをDockerに伝える
EXPOSE 8000

# Webサーバー(Gunicorn)を起動
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.Attendance:application"]