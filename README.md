# Aurafinity full-stack application starter

A **Compact-profile** reference starter implementing an authenticated, tenant-scoped work-item vertical slice. Browser traffic uses a same-origin TanStack Start BFF; FastAPI owns validation, authorization and persistence; PostgreSQL enforces FORCE RLS. No Foundation runtime, AI agents, workers or external providers are activated.

## Start

Requirements: Docker Compose v2 and Docker. Copy `.env.example` to `.env`, set unique strong `JWT_SECRET` and `SESSION_SECRET` values (32+ characters), then run `docker compose up --build`. Open http://localhost:3000.

Provision a local account via an **ephemeral maintenance container** (not the long-running API identity): `docker compose run --rm -e DATABASE_ADMIN_URL=postgresql://postgres:local-postgres-only@db:5432/starter api python -m starter.bootstrap demo@example.test 'choose-a-strong-password'`. Never grant owner/database superuser credentials to the serving API container. Local bootstrap credentials and the example DB password are development-only. This creates a tenant and a member, if missing, with an Argon2 password hash. This provisioning command is strictly an explicit local operation; no known login exists by default.

For development checks run `docker compose exec api pytest -q`. See `docs/acceptance.md` for mandatory acceptance gates and unverified items.

The code demonstrates the trust boundary, not a production authentication deployment. Replace the local credential provider with a reviewed OIDC/identity adapter before production; configure HTTPS, CSRF policy, session rotation, secret management, threat monitoring and production rollback.

Architecture: `docs/architecture.md`. Handbook authority: merged ai-platform-handbook PR #7.
