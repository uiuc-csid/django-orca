ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}
ARG TARGETARCH

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_CACHE_DIR=/var/cache/pypoetry

# Configure apt and install packages
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        sudo \
        postgresql-client \
 && apt clean \
 && rm -rf /var/lib/apt/lists/*

ENV DEBIAN_FRONTEND=dialog
WORKDIR /workspace/app
