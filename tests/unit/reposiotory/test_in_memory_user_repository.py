from tests.builders.user_builder import UserBuilder


def test_add_and_get_user(user_repo):
    user = UserBuilder().build()

    user_repo.add(user)

    assert user_repo.get(user.id) == user

import pytest

def test_add_duplicate_user_id_raises(user_repo):
    user = UserBuilder().build()

    user_repo.add(user)

    with pytest.raises(ValueError):
        user_repo.add(user)

def test_login_must_be_unique(user_repo):
    u1 = UserBuilder().with_login("admin").build()
    u2 = UserBuilder().with_login("admin").build()

    user_repo.add(u1)

    with pytest.raises(ValueError):
        user_repo.add(u2)

def test_list_active_only(user_repo):
    active = UserBuilder().with_is_active(True).build()
    inactive = UserBuilder().with_is_active(False).build()

    user_repo.add(active)
    user_repo.add(inactive)

    result = user_repo.list_contracts(active_only=True)

    assert result == [active]
