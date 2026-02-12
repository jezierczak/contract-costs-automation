from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now

from contract_costs.model.identity.user import User


def build_user(
    *,
    login="jarek",
    email:str|None="jarek@example.com",
    full_name:str|None="Jarosław",
    is_active=True,
):
    return User(
        id=new_uuid(),
        login=login,
        email=email,
        full_name=full_name,
        is_active=is_active,
        created_at=utc_now(),
        created_by_user_id=None,
        updated_at=None,
        updated_by_user_id=None,
        password_hash=None,
        last_login_at=None,
    )

def test_user_creation():
    user = build_user()

    assert user.login == "jarek"
    assert user.is_active is True
    assert user.updated_at is None
    assert user.password_hash is None

import pytest

def test_user_is_immutable():
    user = build_user()

    with pytest.raises(Exception):
        user.login = "admin"

def test_user_defaults():
    user = build_user(email=None, full_name=None)

    assert user.email is None
    assert user.full_name is None

def test_user_equality():
    now = utc_now()
    user_id = new_uuid()

    u1 = User(
        id=user_id,
        login="x",
        email=None,
        full_name=None,
        is_active=True,
        created_at=now,
        created_by_user_id=None,
    )

    u2 = User(
        id=user_id,
        login="x",
        email=None,
        full_name=None,
        is_active=True,
        created_at=now,
        created_by_user_id=None,
    )

    assert u1 == u2
