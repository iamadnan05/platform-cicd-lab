# Operational Runbook — Platform CI/CD Lab

Use this runbook to deploy, monitor, troubleshoot, and roll back the containerized stack.

## 1. Prerequisites & Configuration

* **Required tools:** Docker Engine + Docker Compose v2 (`docker compose version`).
* **Environment variables:** Credentials live in a local `.env` file (excluded from Git via `.gitignore`). Use `.env.example` as the template:
  * `POSTGRES_USER` — PostgreSQL username
  * `POSTGRES_PASSWORD` — PostgreSQL password (never commit real credentials)
  * `POSTGRES_DB` — Target database name

## 2. Standard Deployment & Update

```bash
# Pull latest changes and rebuild/restart services
git pull origin main
docker compose up -d --build

# Confirm all 4 containers are up and db is healthy
docker compose ps
```

## 3. Health Checks & Routine Diagnostics

```bash
# Check end-to-end health (Nginx -> API -> PostgreSQL)
curl -i http://localhost:8080/health

# View real-time logs for a specific service
docker compose logs -f --tail=50 api
docker compose logs -f --tail=50 nginx
docker compose logs -f --tail=50 db

# Check container resource usage (CPU / Memory)
docker stats --no-stream

# Verify the API container runs as non-root
docker exec platform-api whoami
```

## 4. Common Failure Scenarios & Fixes

### Scenario A: `/health` returns `HTTP 500` (`"status": "unhealthy"`)
* **Likely cause:** PostgreSQL container is stopped, unhealthy, or `.env` credentials do not match the existing volume.
* **Diagnosis:**
  ```bash
  docker compose ps
  docker compose logs --tail=50 db
  ```
* **Fix:** Restart the database container and re-test:
  ```bash
  docker compose restart db
  curl http://localhost:8080/health
  ```

### Scenario B: Nginx returns `502 Bad Gateway`
* **Likely cause:** Nginx is running, but the `api` container crashed or failed to bind to `0.0.0.0:8000`.
* **Diagnosis:**
  ```bash
  docker compose logs --tail=50 api
  ```
* **Fix:** Resolve the startup error shown in Gunicorn logs, then rebuild and restart the API:
  ```bash
  docker compose up -d --build api
  ```

### Scenario C: `Bind for 0.0.0.0:8080 failed: port is already allocated`
* **Likely cause:** Another process or leftover container is already using port `8080` on the host.
* **Fix:** Stop conflicting containers (`docker ps`) or change the host port mapping in `docker-compose.yml` (e.g., `"8081:80"`).

## 5. Rollback Procedure (Using GHCR Commit SHA)

Every merge to `main` pushes an immutable image tagged with its Git commit SHA to GitHub Container Registry (`ghcr.io/<owner>/platform-cicd-lab:<commit-sha>`).

1. Find the last known-good commit SHA in GitHub Actions or via `git log --oneline -n 5`.
2. Pull the previous working image directly from GHCR:
   ```bash
   docker pull ghcr.io/<owner>/platform-cicd-lab:<previous-good-sha>
   ```
3. In `docker-compose.yml`, temporarily replace `build: .` under `api:` with `image: ghcr.io/<owner>/platform-cicd-lab:<previous-good-sha>` and redeploy:
   ```bash
   docker compose up -d api
   curl http://localhost:8080/health
   ```
4. Once service is restored, run `git revert <bad-commit-sha>` and push to `main` so Git stays the single source of truth.