"""PostgreSQL implementation; tenant context is transaction-local and parameterized."""
import os
import uuid
from contextlib import contextmanager

import psycopg
from psycopg.rows import dict_row

from .domain import Item


@contextmanager
def connection():
    with psycopg.connect(os.environ["DATABASE_URL"], row_factory=dict_row) as db:
        yield db


class PostgresMemberships:
    def __init__(self, db):
        self.db = db

    def belongs_to(self, user_id: str, tenant_id: str) -> bool:
        row = self.db.execute(
            "SELECT 1 FROM starter.memberships WHERE user_id=%s AND tenant_id=%s",
            (user_id, tenant_id),
        ).fetchone()
        return row is not None


class PostgresItems:
    def __init__(self, db):
        self.db = db

    def _scope(self, tenant_id: str):
        # SET LOCAL semantics; never persist tenant identity across pooled transactions.
        self.db.execute("SELECT set_config('app.tenant_id', %s, true)", (tenant_id,))

    def list_for(self, tenant_id: str) -> list[Item]:
        self._scope(tenant_id)
        rows = self.db.execute(
            "SELECT id,tenant_id,title,revision FROM starter.items ORDER BY created_at DESC"
        ).fetchall()
        return [Item(**{k: str(v) if k in ('id','tenant_id') else v for k,v in row.items()}) for row in rows]

    def create(self, tenant_id: str, user_id: str, title: str) -> Item:
        self._scope(tenant_id)
        item_id = str(uuid.uuid4())
        row = self.db.execute(
            """INSERT INTO starter.items(id,tenant_id,title,created_by)
               VALUES (%s,%s,%s,%s)
               RETURNING id,tenant_id,title,revision""",
            (item_id,tenant_id,title,user_id),
        ).fetchone()
        return Item(str(row["id"]),str(row["tenant_id"]),row["title"],row["revision"])
