"""FastAPI composition root; all tenant decisions are server-enforced."""
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, EmailStr, Field
from pwdlib import PasswordHash

from .application import Forbidden, Principal, create_item, list_items
from .domain import InvalidTitle
from .persistence import PostgresItems, PostgresMemberships, connection

app = FastAPI(title="Aurafinity App Starter", version="0.1.0")
password_hasher = PasswordHash.recommended()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str


class CreateItemRequest(BaseModel):
    title: str = Field(min_length=1, max_length=120)


class TenantResponse(BaseModel):
    id: uuid.UUID
    name: str


class ItemResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    title: str
    revision: int


def current_principal(authorization: str | None = Header(default=None)) -> Principal:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="unauthenticated")
    try:
        payload = jwt.decode(authorization[7:], os.environ["JWT_SECRET"], algorithms=["HS256"], issuer="aurafinity-starter", audience="starter-api")
        return Principal(str(uuid.UUID(payload["sub"])))
    except (jwt.PyJWTError, ValueError, KeyError):
        raise HTTPException(status_code=401, detail="unauthenticated") from None


@app.post("/auth/login", response_model=TokenResponse)
def login(credentials: LoginRequest):
    with connection() as db:
        user = db.execute("SELECT id,password_hash FROM starter.users WHERE email=%s", (credentials.email.lower(),)).fetchone()
        if not user or not password_hasher.verify(credentials.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="invalid_credentials")
        now = datetime.now(timezone.utc)
        claims = {"sub": str(user["id"]), "iss": "aurafinity-starter", "aud": "starter-api", "iat": now, "exp": now + timedelta(minutes=30)}
        return TokenResponse(access_token=jwt.encode(claims,os.environ["JWT_SECRET"],algorithm="HS256"))


@app.get("/tenants", response_model=list[TenantResponse])
def tenants(principal: Annotated[Principal, Depends(current_principal)]):
    with connection() as db:
        return db.execute(
            "SELECT t.id,t.name FROM starter.tenants t JOIN starter.memberships m ON m.tenant_id=t.id WHERE m.user_id=%s ORDER BY t.name",
            (principal.user_id,),
        ).fetchall()


@app.get("/tenants/{tenant_id}/items", response_model=list[ItemResponse])
def get_items(tenant_id: uuid.UUID, principal: Annotated[Principal, Depends(current_principal)]):
    with connection() as db:
        try:
            return list_items(principal,str(tenant_id),PostgresMemberships(db),PostgresItems(db))
        except Forbidden:
            raise HTTPException(status_code=403, detail="forbidden") from None


@app.post("/tenants/{tenant_id}/items", response_model=ItemResponse, status_code=201)
def post_item(tenant_id: uuid.UUID, command: CreateItemRequest, principal: Annotated[Principal, Depends(current_principal)]):
    with connection() as db:
        try:
            return create_item(principal,str(tenant_id),command.title,PostgresMemberships(db),PostgresItems(db))
        except Forbidden:
            raise HTTPException(status_code=403, detail="forbidden") from None
        except InvalidTitle:
            raise HTTPException(status_code=422, detail="invalid_title") from None


@app.get("/health")
def health():
    return {"status":"ok"}
