#!/bin/bash
# Corre en la EC2: descarga el zip de un release y reinicia la app con esa versión.
# Uso: deploy.sh <tag> <owner/repo>
set -euo pipefail

TAG="$1"
REPO="$2"
APP_DIR=/opt/todo-api
NAME="to-do-list-api-$TAG"
RELEASE_DIR="$APP_DIR/releases/$TAG"

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

curl -fsSL -o "$TMP/$NAME.zip" "https://github.com/$REPO/releases/download/$TAG/$NAME.zip"
unzip -q "$TMP/$NAME.zip" -d "$TMP"

rm -rf "$RELEASE_DIR"
mv "$TMP/$NAME" "$RELEASE_DIR"
"$APP_DIR/venv/bin/pip" install -q -r "$RELEASE_DIR/requirements.txt"

ln -sfn "$RELEASE_DIR" "$APP_DIR/current"
sudo sed -i "s/^APP_VERSION=.*/APP_VERSION=$TAG/" /etc/todo-api.env
sudo systemctl restart todo-api

echo "Desplegado $TAG"
