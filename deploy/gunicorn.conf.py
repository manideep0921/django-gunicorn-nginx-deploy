import multiprocessing
import os

bind = os.environ.get('GUNICORN_BIND', 'unix:/run/notes/gunicorn.sock')
workers = int(os.environ.get('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
timeout = 30
graceful_timeout = 30
max_requests = 1000          # recycle workers to limit memory growth
max_requests_jitter = 100
accesslog = '-'
errorlog = '-'
