"""Application layer — explicit principal, membership and persistence ports."""
from dataclasses import dataclass
from typing import Protocol
from .domain import Item, validate_title


class Forbidden(Exception):
    pass


@dataclass(frozen=True)
class Principal:
    user_id: str


class ItemRepository(Protocol):
    def list_for(self, tenant_id: str) -> list[Item]: ...
    def create(self, tenant_id: str, user_id: str, title: str) -> Item: ...


class MembershipRepository(Protocol):
    def belongs_to(self, user_id: str, tenant_id: str) -> bool: ...


def list_items(principal: Principal, tenant_id: str, members: MembershipRepository, items: ItemRepository) -> list[Item]:
    if not members.belongs_to(principal.user_id, tenant_id):
        raise Forbidden()
    return items.list_for(tenant_id)


def create_item(principal: Principal, tenant_id: str, title: str, members: MembershipRepository, items: ItemRepository) -> Item:
    if not members.belongs_to(principal.user_id, tenant_id):
        raise Forbidden()
    return items.create(tenant_id, principal.user_id, validate_title(title))
