# Architecture and constraints

Authority: ai-platform-handbook merged PR #7. Delivery: **template repository**, Compact profile. No generator or application-specific Events entities.

## Trust chain

Browser → same-origin TanStack Start BFF → bearer-authenticated FastAPI → application services/ports → PostgreSQL items table with tenant FORCE RLS.

Browser only receives an HttpOnly SameSite=Lax session cookie. The BFF never exposes the API bearer token in JSON. FastAPI validates issuer, audience, signature and expiration, resolves membership from authoritative database state for each request, and applies transaction-local RLS context. Never trust a browser-provided tenant for authorization. Tenant IDs are selectors, not credentials. A separate non-owner, NOBYPASSRLS database role is used by the API.

## Layers

- Domain: pure title validation and item value.
- Application: membership and item repository protocols, use cases, permission enforcement.
- Infrastructure: psycopg mappings, scoped transactions.
- API: FastAPI endpoints, typed contracts, auth mapping.
- BFF: same-origin cookie session and internal API proxy. No domain rules.
- UI: responsive accessible sign-in/list/create states.

## Routes

| Route | State |
| --- | --- |
| / | loading, login, empty, list, saving, denied, expired, error |
| /bff/session | login, logout; no third-party redirects |
| /bff/tenants | authenticated workspace discovery |
| /bff/items | authenticated read/create; selected tenant |
| FastAPI /auth/login, /tenants, /tenants/{id}/items | private upstream endpoints |

## Production decisions left open

OIDC adapter, robust CSRF controls for cookie-based same-origin mutations (Origin validation and CSRF tokens), logout/token revocation, session rotation and rate limiting; external hosting/networking, TLS and secrets, backups and disaster recovery, migration runner, audit/retention policy and observability. Starter is **not production accepted**. Do not expose port 8000 to the public. Avoid using this example as proof of tenant safety until PostgreSQL negative integration gates pass.

No Foundation runtime calls are needed for this slice. A future adapter must use reviewed public versioned contracts, explicit authorization and independent operational acceptance.
