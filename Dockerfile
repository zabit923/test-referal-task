FROM python:3.11-alpine

RUN apk update && apk add --no-cache \
    bash \
    curl \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    postgresql-dev

# Устанавливаем Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    export PATH="/root/.local/bin:$PATH"

ENV POETRY_VIRTUALENVS_CREATE=false

COPY pyproject.toml poetry.lock /src/
WORKDIR /src

RUN /root/.local/bin/poetry install --no-root

COPY ./src /src

EXPOSE 8000

CMD ["sh", "-c", "/root/.local/bin/poetry run alembic upgrade head && /root/.local/bin/poetry run uvicorn app:app --host 0.0.0.0 --port 8000 --reload"]
