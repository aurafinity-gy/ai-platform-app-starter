-- Bootstrap runs as postgres only; app role is deliberately NON-BYPASSRLS and not the table owner.
CREATE ROLE starter LOGIN PASSWORD 'starter' NOBYPASSRLS;
CREATE SCHEMA starter AUTHORIZATION postgres;
CREATE TABLE starter.users (
 id uuid PRIMARY KEY, email text NOT NULL UNIQUE, password_hash text NOT NULL
);
CREATE TABLE starter.tenants (
 id uuid PRIMARY KEY, name text NOT NULL
);
CREATE TABLE starter.memberships (
 tenant_id uuid NOT NULL REFERENCES starter.tenants(id),
 user_id uuid NOT NULL REFERENCES starter.users(id),
 role text NOT NULL CHECK (role IN ('owner','member')),
 PRIMARY KEY (tenant_id,user_id)
);
CREATE TABLE starter.items (
 id uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES starter.tenants(id),
 title text NOT NULL CHECK (length(trim(title)) BETWEEN 1 AND 120),
 revision integer NOT NULL DEFAULT 1 CHECK (revision >= 1),
 created_by uuid NOT NULL REFERENCES starter.users(id),
 created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX ON starter.items(tenant_id,created_at DESC);
ALTER TABLE starter.items ENABLE ROW LEVEL SECURITY;
ALTER TABLE starter.items FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_items ON starter.items TO starter
 USING (tenant_id = nullif(current_setting('app.tenant_id', true),'')::uuid)
 WITH CHECK (tenant_id = nullif(current_setting('app.tenant_id', true),'')::uuid);
GRANT USAGE ON SCHEMA starter TO starter;
GRANT SELECT ON starter.users,starter.tenants,starter.memberships TO starter;
GRANT SELECT,INSERT,UPDATE ON starter.items TO starter;
-- Bootstrap is restricted to maintenance role, not the serving API identity.
