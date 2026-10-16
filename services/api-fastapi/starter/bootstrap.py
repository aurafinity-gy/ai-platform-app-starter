"""Explicit local maintenance bootstrap; requires database owner credentials."""
import os
import sys
import uuid

import psycopg
from pwdlib import PasswordHash


def main():
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python -m starter.bootstrap email password")
    email, password = sys.argv[1:]
    if len(password) < 12:
        raise SystemExit("Password must contain at least 12 characters")
    admin_url = os.environ.get("DATABASE_ADMIN_URL")
    if not admin_url:
        raise SystemExit("DATABASE_ADMIN_URL required (owner-only operation)")
    hasher = PasswordHash.recommended()
    with psycopg.connect(admin_url) as db:
        row = db.execute("SELECT id FROM starter.users WHERE email=%s", (email.lower(),)).fetchone()
        if row:
            raise SystemExit("Account exists; no password reset via bootstrap")
        user_id, tenant_id = uuid.uuid4(), uuid.uuid4()
        db.execute("INSERT INTO starter.users(id,email,password_hash) VALUES (%s,%s,%s)",
                   (user_id,email.lower(),hasher.hash(password)))
        db.execute("INSERT INTO starter.tenants(id,name) VALUES (%s,%s)",(tenant_id,"My workspace"))
        db.execute("INSERT INTO starter.memberships(tenant_id,user_id,role) VALUES (%s,%s,'owner')",(tenant_id,user_id))
    print("Account and workspace created")


if __name__ == "__main__":
    main()
