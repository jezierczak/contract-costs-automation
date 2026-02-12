from datetime import datetime
from typing import Any
from uuid import UUID

from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now
from contract_costs.model.identity.organization import Organization


class OrganizationBuilder:
    def __init__(self):
        now = utc_now()

        self._id: UUID = new_uuid()
        self._code: str = "TESTORG"
        self._name: str = "Test Organization"

        self._is_active: bool = True

        self._created_at: datetime = now
        self._created_by_user_id: UUID | None = None

        self._updated_at: datetime | None = None
        self._updated_by_user_id: UUID | None = None

        self._settings: dict[str, Any] | None = None

    # ---------------------------
    # identity
    # ---------------------------

    def with_id(self, id_: UUID):
        self._id = id_
        return self

    def with_code(self, code: str):
        self._code = code
        return self

    def with_name(self, name: str):
        self._name = name
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

    def with_created_at(self, dt: datetime):
        self._created_at = dt
        return self

    def with_created_by(self, user_id: UUID | None):
        self._created_by_user_id = user_id
        return self

    def with_updated(self, updated_at: datetime, updated_by: UUID | None):
        self._updated_at = updated_at
        self._updated_by_user_id = updated_by
        return self

    # ---------------------------
    # settings
    # ---------------------------

    def with_settings(self, settings: dict[str, Any] | None):
        self._settings = settings
        return self

    # ---------------------------
    # build
    # ---------------------------

    def build(self) -> Organization:
        return Organization(
            id=self._id,
            code=self._code,
            name=self._name,
            is_active=self._is_active,
            created_at=self._created_at,
            created_by_user_id=self._created_by_user_id,
            updated_at=self._updated_at,
            updated_by_user_id=self._updated_by_user_id,
            settings=self._settings,
        )
