FROM ghcr.io/astral-sh/uv:python3.14-alpine

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /app

COPY pyproject.toml uv.lock /app/
RUN uv sync --frozen --no-dev --no-cache --no-install-project

COPY . /app
RUN uv sync --frozen --no-dev --no-cache

ENV UV_NO_SYNC=1
ENV UV_OFFLINE=1

CMD [ "uv", "run", "ug-calendar-exporter" ]
