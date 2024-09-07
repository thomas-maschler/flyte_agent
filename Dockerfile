FROM python:3.12-slim-bookworm

ARG POETRY_VERSION=1.8.3
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME=/opt/poetry \
    POETRY_VERION=${POETRY_VERSION} \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

RUN apt-get update && apt-get install build-essential curl -y
RUN curl -sSL https://install.python-poetry.org | python3 -

ENV ENV=/opt/custom_job
WORKDIR ${ENV}

COPY pyproject.toml poetry.lock ${ENV}
COPY flyte_agent ${ENV}/flyte_agent

RUN touch README.md
RUN --mount=type=cache,target=${POETRY_CACHE_DIR} \
    $POETRY_HOME/bin/poetry install 

ENV PATH="${ENV}/.venv/bin:$PATH"
CMD pyflyte serve agent --port 8000