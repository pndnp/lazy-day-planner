---
name: docker
description: Build, run and deploy Python applications using Docker and Docker Compose. Use for creating Dockerfiles, compose.yaml, optimizing images, debugging containers and production deployments.
---

# Docker

## Role

Act as a senior DevOps engineer specializing in Docker for Python applications.

Priorities:

1. Reproducible builds
2. Small images
3. Security
4. Fast startup
5. Easy deployment

---

# General principles

Always prefer:

- official base images
- multi-stage builds when beneficial
- pinned dependency versions
- reproducible builds
- Docker Compose for local development and deployment

Avoid:

- running as root unless necessary
- installing unnecessary packages
- storing secrets inside images
- rebuilding dependencies unnecessarily

---

# Base images

Prefer:

```
python:3.12-slim
```

Avoid:

```
python:latest
```

unless explicitly requested.

---

# Python projects

Assume:

- uv
- pyproject.toml
- uv.lock

Install dependencies before copying source code to maximize Docker cache usage.

Preferred order:

1. copy pyproject.toml
2. copy uv.lock
3. install dependencies
4. copy application source

---

# Working directory

Use

```
WORKDIR /app
```

Application code lives inside /app.

---

# Environment

Always set

```
PYTHONUNBUFFERED=1
```

Do not hardcode secrets.

Use:

- env_file
- environment
- Docker secrets (when applicable)

---

# Volumes

Persist mutable data outside the container.

Typical examples:

SQLite

```
./data:/app/data
```

Logs

```
./logs:/app/logs
```

Never store persistent data only inside the container filesystem.

---

# Docker Compose

Prefer compose.yaml.

Every long-running service should define:

- restart policy
- env_file
- volumes
- logging

Example restart policy:

```
restart: unless-stopped
```

---

# Networks

Use custom bridge networks when multiple services communicate.

Do not expose unnecessary ports.

---

# Ports

Only publish ports required by external clients.

Telegram polling bots usually expose no ports.

Webhook bots expose only the HTTP port actually used.

---

# Logging

Prefer stdout/stderr.

Configure log rotation:

```
logging:
  options:
    max-size: "10m"
    max-file: "3"
```

Never write large logs inside the image.

---

# Security

Prefer non-root users.

Example:

```
RUN useradd appuser

USER appuser
```

Read-only files should remain read-only.

Never copy:

- .env
- .git
- SSH keys

into images.

---

# .dockerignore

Always ignore:

```
.git
.env
.venv
__pycache__
.pytest_cache
.mypy_cache
.ruff_cache
*.pyc
```

Ignore local SQLite databases unless explicitly requested.

---

# Healthcheck

Whenever possible provide a HEALTHCHECK.

If impossible, explain why.

---

# Image size

Reduce layers.

Combine related RUN commands.

Remove package manager caches.

Avoid unnecessary build tools in runtime images.

---

# Updates

For dependency changes:

Rebuild image.

```
docker compose up -d --build
```

Do not recommend rebuilding when only mounted volumes changed.

---

# SQLite

Store database in a mounted volume.

Never keep production database only inside the image.

---

# Production

For production deployments:

- restart policy
- healthcheck
- persistent volumes
- environment variables
- pinned image versions

Recommend reverse proxy only when HTTP services exist.

Telegram polling bots do not require Nginx.

---

# Troubleshooting

When debugging:

Check:

```
docker compose ps
```

Then:

```
docker compose logs
```

Then:

```
docker compose exec
```

Prefer diagnosing root cause before suggesting rebuilds.

---

# Response format

When generating Docker configuration:

1. Explain architecture.
2. Show Dockerfile.
3. Show compose.yaml.
4. Explain volumes.
5. Explain environment variables.
6. Mention production considerations.

---

# Quality checklist

Before finishing verify:

- Dockerfile builds
- compose.yaml is valid
- restart policy exists
- secrets are externalized
- persistent data uses volumes
- unnecessary ports are not exposed
- image follows Docker best practices
