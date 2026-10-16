import pytest
from starter.domain import validate_title, InvalidTitle
from starter.application import Principal, Forbidden, create_item, list_items


class Members:
    def __init__(self, allow):
        self.allow = allow
    def belongs_to(self, user_id, tenant_id):
        return self.allow


class Items:
    def __init__(self):
        self.created = []
    def create(self, tenant_id, user_id, title):
        self.created.append((tenant_id,user_id,title))
        return title
    def list_for(self, tenant_id):
        return ["visible"]


def test_title_normalization():
    assert validate_title("  Hello  ") == "Hello"


@pytest.mark.parametrize("value",["","  ","x"*121])
def test_invalid_titles(value):
    with pytest.raises(InvalidTitle):
        validate_title(value)


def test_denied_command_never_reaches_repository():
    items = Items()
    with pytest.raises(Forbidden):
        create_item(Principal("other"),"tenant","Hello",Members(False),items)
    assert items.created == []


def test_denied_query():
    with pytest.raises(Forbidden):
        list_items(Principal("other"),"tenant",Members(False),Items())


def test_allowed_create_and_list():
    items = Items()
    assert create_item(Principal("me"),"tenant"," ok ",Members(True),items) == "ok"
    assert items.created == [("tenant","me","ok")]
    assert list_items(Principal("me"),"tenant",Members(True),items) == ["visible"]
