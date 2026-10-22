# django-gunicorn-nginx-deploy

A small Django notes API deployed the traditional way on Ubuntu:
**Nginx -> Gunicorn (unix socket) -> Django -> PostgreSQL**, managed by systemd.

## What's included
| Path | Purpose |
|---|---|
| `notes/` | JSON API (`GET/POST /api/notes`) plus `/healthz` (liveness) and `/readyz` (DB readiness) |
| `config/settings.py` | 12-factor config from env vars; SQLite for local dev, PostgreSQL when `DB_HOST` is set; WhiteNoise static files; proxy/TLS headers |
| `deploy/gunicorn.conf.py` | Workers, timeouts, worker recycling |
| `deploy/notes.service` | systemd unit (restart on failure, sandboxing options) |
| `deploy/nginx.conf` | Reverse proxy to the Gunicorn socket, static files |
| `deploy/deploy.sh` | Idempotent server deploy: packages, venv, migrate, collectstatic, services, smoke test |
| `deploy/env.example` | Environment file template (copied to `/etc/notes/env`) |

## Run locally
```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py test
GUNICORN_BIND=127.0.0.1:8000 gunicorn -c deploy/gunicorn.conf.py config.wsgi:application
curl localhost:8000/healthz
```

## Deploy to Ubuntu
```bash
sudo ./deploy/deploy.sh          # first run creates /etc/notes/env, edit it, then re-run
sudo systemctl status notes
sudo journalctl -u notes -f
```
Create the database first:
```sql
CREATE USER notes WITH PASSWORD '...'; CREATE DATABASE notes OWNER notes;
```
Add HTTPS with `certbot --nginx` and set `DJANGO_HTTPS=1`.
