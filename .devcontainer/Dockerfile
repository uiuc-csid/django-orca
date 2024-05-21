ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}
ARG TARGETARCH
ARG NODE_MAJOR=20

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_CACHE_DIR=/var/cache/pypoetry

# Configure apt and install packages
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        sudo \
        postgresql-client

# Setup nodesource
RUN mkdir -p /etc/apt/keyrings \
 && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
 && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list \
 && apt-get update \
 && apt-get install -y nodejs

ENV DEBIAN_FRONTEND=dialog
WORKDIR /workspace/app
