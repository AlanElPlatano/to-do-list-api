#!/bin/bash
set -euxo pipefail

apt-get update -y
apt-get install -y git python3-venv postgresql-client unzip

# Cada versión vive en releases/<versión>; "current" apunta a la que corre
APP_DIR=/opt/todo-api
git clone ${repo_url} $APP_DIR/releases/bootstrap
VERSION=$(git -C $APP_DIR/releases/bootstrap describe --tags --always)
python3 -m venv $APP_DIR/venv
$APP_DIR/venv/bin/pip install -r $APP_DIR/releases/bootstrap/requirements.txt
ln -sfn $APP_DIR/releases/bootstrap $APP_DIR/current
chown -R ubuntu:ubuntu $APP_DIR

# La app solo recibe el nombre del secreto, nunca la contraseña.
# El workflow de deploy actualiza APP_VERSION en cada release.
cat > /etc/todo-api.env <<EOF
AWS_REGION=${region}
DB_SECRET_NAME=${db_secret_name}
APP_VERSION=$VERSION
EOF

cat > /etc/systemd/system/todo-api.service <<EOF
[Unit]
Description=To-do list API
After=network-online.target
Wants=network-online.target

[Service]
User=ubuntu
WorkingDirectory=$APP_DIR/current
EnvironmentFile=/etc/todo-api.env
ExecStart=$APP_DIR/venv/bin/gunicorn --workers 2 --bind 0.0.0.0:${app_port} "app:create_app()"
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now todo-api
