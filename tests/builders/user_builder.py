from datetime import datetime
from uuid import UUID, uuid4

from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now
from contract_costs.model.identity.user import User


class UserBuilder:
    def __init__(self):
        now = utc_now()

        self._id: UUID = new_uuid()

        self._login = f"user_{uuid4().hex[:6]}"
        self._email: str | None = "test@example.com"
        self._full_name: str | None = "Test User"

        self._is_active: bool = True

        self._created_at: datetime = now
        self._created_by_user_id: UUID | None = None

        self._updated_at: datetime | None = None
        self._updated_by_user_id: UUID | None = None

        self._password_hash: str | None = None
        self._last_login_at: datetime | None = None

    # ---------------------------
    # identity
    # ---------------------------

    def with_id(self, id_: UUID):
        self._id = id_
        return self

    def with_login(self, login: str):
        self._login = login
        return self

    def with_email(self, email: str | None):
        self._email = email
        return self

    def with_full_name(self, full_name: str | None):
        self._full_name = full_name
        return self

    # ---------------------------
    # status
    # ---------------------------

    def with_is_active(self, value: bool):
        self._is_active = value
        return self

    def inactive(self):
        self._is_active = False
        return self

    # ---------------------------
    # audit
    # ---------------------------

    def with_created(self, at: datetime, by: UUID | None):
        self._created_at = at
        self._created_by_user_id = by
        return self

    def with_updated(self, at: datetime, by: UUID | None):
        self._updated_at = at
        self._updated_by_user_id = by
        return self

    # ---------------------------
    # auth fields
    # ---------------------------

    def with_password_hash(self, password_hash: str | None):
        self._password_hash = password_hash
        return self

    def with_last_login(self, last_login_at: datetime | None):
        self._last_login_at = last_login_at
        return self

    # ---------------------------
    # build
    # ---------------------------

    def build(self) -> User:
        return User(
            id=self._id,
            login=self._login,
            email=self._email,
            full_name=self._full_name,
            is_active=self._is_active,
            created_at=self._created_at,
            created_by_user_id=self._created_by_user_id,
            updated_at=self._updated_at,
            updated_by_user_id=self._updated_by_user_id,
            password_hash=self._password_hash,
            last_login_at=self._last_login_at,
        )
