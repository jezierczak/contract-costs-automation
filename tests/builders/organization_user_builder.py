from datetime import datetime
from uuid import UUID

from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now
from contract_costs.model.identity.organization_user import OrganizationUser
from contract_costs.model.identity.organization_role import OrganizationRole


class OrganizationUserBuilder:
    def __init__(self):
        now = utc_now()

        self._id: UUID = new_uuid()
        self._organization_id: UUID = new_uuid()
        self._user_id: UUID = new_uuid()

        self._role: OrganizationRole = OrganizationRole.USER
        self._is_active: bool = True

        self._created_at: datetime = now
        self._created_by_user_id: UUID | None = None

        self._updated_at: datetime | None = None
        self._updated_by_user_id: UUID | None = None

        self._invited_at: datetime | None = None
        self._invited_by_user_id: UUID | None = None
        self._accepted_at: datetime | None = None

    # ---------------------------
    # identity
    # ---------------------------

    def with_id(self, id_: UUID):
        self._id = id_
        return self

    def with_organization_id(self, organization_id: UUID):
        self._organization_id = organization_id
        return self

    def with_user_id(self, user_id: UUID):
        self._user_id = user_id
        return self

    # ---------------------------
    # role
    # ---------------------------

    def with_role(self, role: OrganizationRole):
        self._role = role
        return self

    def as_admin(self):
        self._role = OrganizationRole.ADMIN
        return self

    def as_owner(self):
        self._role = OrganizationRole.OWNER
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
    # invite flow
    # ---------------------------

    def invited(self, at: datetime, by: UUID):
        self._invited_at = at
        self._invited_by_user_id = by
        return self

    def accepted(self, at: datetime):
        self._accepted_at = at
        return self

    # ---------------------------
    # build
    # ---------------------------

    def build(self) -> OrganizationUser:
        return OrganizationUser(
            id=self._id,
            organization_id=self._organization_id,
            user_id=self._user_id,
            role=self._role,
            is_active=self._is_active,
            created_at=self._created_at,
            created_by_user_id=self._created_by_user_id,
            updated_at=self._updated_at,
            updated_by_user_id=self._updated_by_user_id,
            invited_at=self._invited_at,
            invited_by_user_id=self._invited_by_user_id,
            accepted_at=self._accepted_at,
        )
