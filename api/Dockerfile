FROM python:3.12.7-slim as builder

LABEL maintainer="aurelio"
LABEL vendor="aurelio"

ARG DOCKER_IMAGE_TAG
ENV PYTHONPATH=/app \
    PYTHONFAULTHANDLER=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_REQUESTS_TIMEOUT=6000\
    PIP_ROOT_USER_ACTION=ignore \
    POETRY_VERSION=2.0.1 \
    POETRY_CACHE_DIR='/var/cache/poetry' \
    LANG=C.UTF-8

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends build-essential linux-headers-generic \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry pip --upgrade

WORKDIR /app
# Copy only requirements and local module to cache them in docker layer
COPY poetry.lock pyproject.toml ./
COPY api ./api
COPY main.py ./main.py
COPY README.md README.md

# Project initialization:
RUN poetry config installer.max-workers 20 \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi \
    && rm -rf $POETRY_CACHE_DIR

FROM builder as runtime
WORKDIR /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--loop", "uvloop"]
