#!/bin/bash
set -euxo pipefail

apt-get update -y
apt-get install -y git python3-venv

APP_DIR=/opt/todo-api
git clone ${repo_url} $APP_DIR
python3 -m venv $APP_DIR/venv
$APP_DIR/venv/bin/pip install -r $APP_DIR/requirements.txt
chown -R ubuntu:ubuntu $APP_DIR

# Un solo worker: las tareas viven en la memoria del proceso
cat > /etc/systemd/system/todo-api.service <<EOF
[Unit]
Description=To-do list API
After=network-online.target
Wants=network-online.target

[Service]
User=ubuntu
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/venv/bin/gunicorn --workers 1 --bind 0.0.0.0:${app_port} app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now todo-api
