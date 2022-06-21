FROM python:3.9.13-slim
WORKDIR /autotagger

# https://github.com/python-poetry/poetry/discussions/1879#discussioncomment-216865
ENV \
  # https://stackoverflow.com/questions/59812009/what-is-the-use-of-pythonunbuffered-in-docker-file
  PYTHONUNBUFFERED=1 \
  # https://python-docs.readthedocs.io/en/latest/writing/gotchas.html#disabling-bytecode-pyc-files
  PYTHONDONTWRITEBYTECODE=1 \
  # https://stackoverflow.com/questions/45594707/what-is-pips-no-cache-dir-good-for
  PIP_NO_CACHE_DIR=1 \
  # https://stackoverflow.com/questions/46288847/how-to-suppress-pip-upgrade-warning
  PIP_DISABLE_PIP_VERSION_CHECK=1 \
  PATH=/autotagger:$PATH

RUN \
  apt-get update && \
  apt-get install -y --no-install-recommends tini build-essential gfortran libatlas-base-dev wget && \
  pip install "poetry==1.1.13"

COPY pyproject.toml poetry.lock ./
RUN \
  python -m poetry install --no-dev && \
  rm -rf /root/.cache/pypoetry/artifacts /root/.cache/pypoetry/cache

RUN \
  mkdir models && \
  wget https://github.com/danbooru/autotagger/releases/download/2022.06.20-233624-utc/model.pth -O models/model.pth

COPY . .

EXPOSE 5000
ENTRYPOINT ["tini", "--", "poetry", "run"]
#CMD ["autotag"]
#CMD ["flask", "run", "--host", "0.0.0.0"]
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
