#!/bin/bash
set -euxo pipefail

apt-get update -y
apt-get install -y git python3-venv postgresql-client

APP_DIR=/opt/todo-api
git clone ${repo_url} $APP_DIR
python3 -m venv $APP_DIR/venv
$APP_DIR/venv/bin/pip install -r $APP_DIR/requirements.txt
chown -R ubuntu:ubuntu $APP_DIR

# La app solo recibe el nombre del secreto, nunca la contraseña
cat > /etc/systemd/system/todo-api.service <<EOF
[Unit]
Description=To-do list API
After=network-online.target
Wants=network-online.target

[Service]
User=ubuntu
WorkingDirectory=$APP_DIR
Environment=AWS_REGION=${region}
Environment=DB_SECRET_NAME=${db_secret_name}
ExecStart=$APP_DIR/venv/bin/gunicorn --workers 2 --bind 0.0.0.0:${app_port} app:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now todo-api
