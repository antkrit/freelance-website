FROM        python:3.11-slim AS builder
WORKDIR     /src

ENV         PYTHONUNBUFFERED=1 \
            PYTHONDONTWRITEBYTECODE=1

RUN         apt-get update \
            && apt-get install --no-install-recommends -y \
                curl \
                build-essential

RUN         pip install --upgrade pip && pip install poetry
RUN         poetry config virtualenvs.in-project true

COPY        pyproject.toml ./
COPY        poetry.lock ./
COPY        README.md ./

RUN         poetry install --no-interaction --no-ansi -vvv --only main --no-root
# ------------------------------------------------------------------------------
FROM        python:3.11-slim AS runtime
WORKDIR     /src

COPY        --from=builder /src .

COPY        freelance_website/ ./freelance_website
COPY        main.py .

EXPOSE      8000

CMD         [".venv/bin/uvicorn", "main:app", "--host", "0.0.0.0"]
