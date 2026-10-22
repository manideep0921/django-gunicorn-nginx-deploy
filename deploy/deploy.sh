#!/usr/bin/env bash
# Deploy the app on an Ubuntu server. Run as a user with sudo.
# Usage: sudo ./deploy/deploy.sh
set -euo pipefail

APP_DIR=/opt/notes
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> packages"
apt-get update -qq
apt-get install -y -qq python3-venv python3-dev libpq-dev nginx postgresql

echo "==> code"
mkdir -p "$APP_DIR" /etc/notes
rsync -a --delete --exclude venv --exclude .git --exclude db.sqlite3 --exclude staticfiles "$SRC"/ "$APP_DIR"/

echo "==> virtualenv + dependencies"
python3 -m venv "$APP_DIR/venv"
"$APP_DIR/venv/bin/pip" install -q -r "$APP_DIR/requirements.txt"

if [[ ! -f /etc/notes/env ]]; then
  cp "$APP_DIR/deploy/env.example" /etc/notes/env
  chmod 640 /etc/notes/env && chown root:www-data /etc/notes/env
  echo "!! Created /etc/notes/env from template. Edit it (secret key, DB password, hosts), then re-run."
  exit 1
fi

echo "==> migrate + collectstatic"
set -a; source /etc/notes/env; set +a
( cd "$APP_DIR" && ./venv/bin/python manage.py migrate --noinput && ./venv/bin/python manage.py collectstatic --noinput )
chown -R www-data:www-data "$APP_DIR/staticfiles"

echo "==> systemd + nginx"
cp "$APP_DIR/deploy/notes.service" /etc/systemd/system/notes.service
cp "$APP_DIR/deploy/nginx.conf" /etc/nginx/sites-available/notes
ln -sf /etc/nginx/sites-available/notes /etc/nginx/sites-enabled/notes
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl daemon-reload
systemctl enable --now notes
systemctl restart notes
systemctl reload nginx

echo "==> smoke test"
sleep 2
curl -fsS http://127.0.0.1/healthz && echo && curl -fsS http://127.0.0.1/readyz && echo
echo "deployed OK"
