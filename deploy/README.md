# Production deployment

A minimal, opinionated stack that terminates TLS at [Caddy](https://caddyserver.com/) and keeps the API + database on an internal Docker network. Caddy handles certificate issuance and renewal automatically via Let's Encrypt — no manual cert files.

## What ships here

- `Caddyfile` — reverse proxy to the API, static file server for the built frontend, HSTS + security headers, gzip/zstd encoding.
- `docker-compose.prod.yml` — Caddy on `:80`/`:443`, FastAPI behind it (no exposed port), Postgres on an internal network only, migrator one-shot.

## Prerequisites

- A server with Docker and Docker Compose v2.
- Two DNS A records pointing at the server, e.g. `api.example.com` and `app.example.com`.
- Ports 80 and 443 reachable from the public internet (Let's Encrypt HTTP-01/TLS-ALPN challenges).

## Setup

1. **Create `.env.prod` at the repo root** (gitignored — `.env*` matches the existing rule). All values are required.

   ```bash
   # Domains + ACME
   ACME_EMAIL=admin@example.com
   API_DOMAIN=api.example.com
   APP_DOMAIN=app.example.com

   # Database
   SOCIALPYKIT_DB_USER=socialpykit
   SOCIALPYKIT_DB_PASS=<long-random-string>
   SOCIALPYKIT_DB_BASE=socialpykit

   # JWT — generate with: python -c "import secrets; print(secrets.token_urlsafe(64))"
   SOCIALPYKIT_JWT_SECRET_KEY=<paste-output-here>
   SOCIALPYKIT_JWT_ALGORITHM=HS256
   SOCIALPYKIT_JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

   # CORS — must match APP_DOMAIN exactly, JSON list
   SOCIALPYKIT_CORS_ORIGINS=["https://app.example.com"]

   # Observability
   SOCIALPYKIT_SENTRY_DSN=
   SOCIALPYKIT_SENTRY_SAMPLE_RATE=0.1
   ```

2. **Build the frontend with the production API URL** (compiled into the bundle at build time):

   ```bash
   cd ui
   VITE_API_BASE_URL=https://api.example.com bun run build
   ```

   This produces `ui/dist/`, which the Caddy container mounts read-only.

3. **Launch the stack** (run from the repo root):

   ```bash
   docker compose --env-file .env.prod -f deploy/docker-compose.prod.yml up -d --build
   ```

4. **Bootstrap the first admin** once the migrator has finished:

   ```bash
   docker compose --env-file .env.prod -f deploy/docker-compose.prod.yml \
     exec api python scripts/promote_admin.py admin@example.com
   ```

## Operations

- **Logs**: `docker compose -f deploy/docker-compose.prod.yml logs -f caddy api`
- **Restart API** (e.g. after config change): `docker compose -f deploy/docker-compose.prod.yml restart api`
- **Migrations**: any new image rebuild re-runs the `migrator` service automatically. To run manually: `docker compose -f deploy/docker-compose.prod.yml run --rm migrator`
- **Certificate storage**: lives in the `caddy-data` Docker volume. Back it up alongside the database.

## Hardening checklist

- [ ] `SOCIALPYKIT_JWT_SECRET_KEY` rotated per environment, never the dev default.
- [ ] `SOCIALPYKIT_DB_PASS` is a long random string, set only via your secret manager.
- [ ] DNS records point only at this server; no wildcard exposing other services.
- [ ] Firewall (UFW / cloud security group) allows only `:22`, `:80`, `:443` inbound.
- [ ] `caddy-data` volume backed up (cert renewal state).
- [ ] Database backed up regularly via `pg_dump` or a managed snapshot policy.
- [ ] Sentry DSN set (or removed) — empty string disables, real DSN enables.
