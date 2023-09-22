# `base` sets up all our shared environment variables
FROM python:3.11.5-slim as python-base
ENV LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    DEBIAN_FRONTEND="noninteractive" \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.6.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYSETUP_PATH="/opt/pysetup"
ENV PATH="$POETRY_HOME/bin:$PATH"
ENV PYTHONPATH="$PYTHONPATH:$PYSETUP_PATH/delta"

# `builder-base` stage is used to build deps + create our virtual environment
FROM python-base as builder-base

# Change apt-repo source and Install build deps
RUN apt-get update && \
    apt-get install --no-install-recommends -y build-essential git curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Install python dependencies
WORKDIR $PYSETUP_PATH
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-interaction --no-ansi --only main

# Copy source code and build cython code
COPY delta ./delta
COPY build.py .
RUN poetry run python build.py

FROM python-base as application
# copy in our built poetry + venv
WORKDIR $PYSETUP_PATH
COPY --from=builder-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH
COPY --from=builder-base /usr/bin /usr/bin
COPY --from=builder-base /usr/local/bin /usr/local/bin
COPY --from=builder-base /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages