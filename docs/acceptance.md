# Validation and acceptance status

Implemented but **unverified at runtime** in this GitHub-only session. No green claim is made.

## Mandatory gates

1. Backend install, ruff check, pytest; dependency/import boundary tests.
2. Postgres migration, grant safety, FORCE RLS assertion, wrong-tenant read/write and role-based denial tests using non-owner app role. Verify connection-pool transaction context isolation.
3. Generate FastAPI OpenAPI JSON using a reproducible script, generate TS types with openapi-typescript; commit outputs and add exact generated-contract drift check (not yet supplied).
4. npm clean install/build/typecheck; TanStack Start route generation and same-origin session handlers.
5. Playwright login, denied, empty, create and logout at desktop/mobile viewport. axe accessibility and keyboard/screen-reader smoke.
6. CSRF and credential stuffing/throttling hardening, cookie security, auth expiration/revocation and session lifecycle.
7. Clean Compose one-command boot with actual DB and seeded account; teardown and restore rehearsal.
8. Exact-head CI, image integrity, security scans, release tagging/rollback and separate operational approval.

## Known implementation gaps

- Initial local bootstrap requires owner-only DATABASE_ADMIN_URL environment; container operator supplies it explicitly.
- Starter does not yet have generated OpenAPI artifact, integrated Postgres RLS tests, Playwright or deployment pipeline.
- Session implementation deliberately compact, not suitable for production without CSRF hardening and OIDC.
- Pinned dependency lockfiles and exact-head CI results not available.
- No merge, stage, production, providers or Foundation activation.
