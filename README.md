# Platform CI/CD & Containerized Stack Lab

A production-style containerized Python microservice behind an Nginx reverse proxy with PostgreSQL persistence, Uptime Kuma health monitoring, automated GitHub Actions CI/CD to GitHub Container Registry (GHCR), and Git-tracked operational runbooks.

## Architecture

```text
Client (:8080) ──▶ Nginx Reverse Proxy (:80) ──▶ Flask/Gunicorn API (:8000) ──▶ PostgreSQL (:5432)
                                                         ▲
Uptime Kuma (:3001) ─────── polls /health ───────────────┘ (over internal Docker network)
```

## Key Platform Engineering Features

* **Multi-Stage Docker Build:** Separates build dependencies (`python:3.11`) from the minimal runtime image (`python:3.11-slim`), excludes dev/test files via `.dockerignore`, and runs as a non-root user (`appuser`) to reduce image size and attack surface.
* **Network Isolation & Persistence:** Only Nginx (`8080:80`) and Uptime Kuma (`3001:3001`) publish host ports. The Python API and PostgreSQL communicate strictly over a private Docker bridge network (`platform_net`), using a named volume (`pgdata`) and a `pg_isready` healthcheck.
* **Automated CI/CD Pipeline:** GitHub Actions runs `flake8` linting and `pytest` unit tests on every push and pull request. On merges to `main`, it authenticates to `ghcr.io` using a least-privilege `GITHUB_TOKEN` and publishes images tagged with the immutable commit SHA and `latest`.
* **Monitoring & Docs-as-Code:** Uptime Kuma continuously monitors `/health` (verifying both API and PostgreSQL connectivity), backed by a Git-versioned `RUNBOOK.md`.

## Quick Start

1. Copy the environment template and set local values:
   ```bash
   # Linux / macOS / Git Bash
   cp .env.example .env

   # Windows cmd
   copy .env.example .env
   ```

2. Build and start the full stack:
   ```bash
   docker compose up -d --build
   ```

3. Verify the API and PostgreSQL connection through Nginx:
   ```bash
   curl http://localhost:8080/health
   ```
   Expected response:
   ```json
   {"database":"connected","status":"healthy"}
   ```

4. Access the Uptime Kuma monitoring dashboard at `http://localhost:3001`.

## Operations & Troubleshooting
See [RUNBOOK.md](./RUNBOOK.md) for deployment steps, diagnostic commands, failure recovery, and rollback procedures.