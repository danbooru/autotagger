from os import getenv
from distutils.util import strtobool

wsgi_app = "app:app"
bind = getenv("GUNICORN_BIND", "0.0.0.0:5000")
workers = int(getenv("GUNICORN_WORKERS", 1))
threads = int(getenv("GUNICORN_THREADS", 4))
accesslog = getenv("GUNICORN_ACCESSLOG", "-")
errorlog = getenv("GUNICORN_ERRORLOG", "-")
loglevel = getenv("GUNICORN_LOGLEVEL", "info")
preload_app = bool(strtobool(getenv("GUNICORN_PRELOAD", "True")))
