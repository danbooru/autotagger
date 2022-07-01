from os import getenv
from distutils.util import strtobool

wsgi_app = "app:app"
bind = getenv("GUNICORN_BIND", "0.0.0.0:5000")
workers = int(getenv("GUNICORN_WORKERS", 1))
threads = int(getenv("GUNICORN_THREADS", 4))
accesslog = getenv("GUNICORN_ACCESSLOG", "-")
errorlog = getenv("GUNICORN_ERRORLOG", "-")
loglevel = getenv("GUNICORN_LOGLEVEL", "info")
access_log_format = getenv("GUNICORN_ACCESS_LOG_FORMAT", '{"time":"%(t)s","id":"%({X-Request-Id}i)s","ip":"%(h)s","method":"%(m)s","url":"%(U)s","status":"%(s)s","contentType":"%(Content-Type)s","userAgent":"%(a)s","referer":"%(f)s","sent":"%(B)s","duration":"%(D)s"}')
preload_app = bool(strtobool(getenv("GUNICORN_PRELOAD", "True")))
max_requests = int(getenv("GUNICORN_MAX_REQUESTS", 0))
max_requests_jitter = int(getenv("GUNICORN_MAX_REQUESTS_JITTER", 0))
