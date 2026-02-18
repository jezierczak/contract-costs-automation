import logging
from dataclasses import dataclass, replace
from datetime import datetime
from uuid import UUID

from contract_costs.model.identity.organization_role import OrganizationRole
from contract_costs.services.identity.exceptions import PermissionDenied


# logger = logging.getLogger(__name__)
@dataclass(frozen=True)
class OrganizationUser:
    id: UUID

    organization_id: UUID
    user_id: UUID

    role: OrganizationRole
    is_active: bool

    # audyt
    created_at: datetime
    created_by_user_id: UUID | None

    updated_at: datetime | None = None
    updated_by_user_id: UUID | None = None

    # zaproszenia / onboarding (na przyszłość)
    invited_at: datetime | None = None
    invited_by_user_id: UUID | None = None
    accepted_at: datetime | None = None

    def accept(self, *, now: datetime, by_user_id: UUID) -> "OrganizationUser":
        if self.role == OrganizationRole.OWNER:
            # logger.info(f"Owner role is accepted from begining")
            return self

        if self.accepted_at is not None:
            # logger.info(f"User already accepted by user {self.user_id} at {self.accepted_at}")
            return self

        return replace(
            self,
            accepted_at=now,
            updated_at=now,
            updated_by_user_id=by_user_id,
        )

    def change_role(
            self,
            *,
            new_role: OrganizationRole,
            actor_role: OrganizationRole,
            now: datetime,
            by_user_id: UUID,
    ) -> "OrganizationUser":

        if self.role == OrganizationRole.OWNER:
            raise PermissionDenied("Cannot change OWNER")

        if new_role == OrganizationRole.OWNER and actor_role != OrganizationRole.OWNER:
            raise PermissionDenied("Only OWNER can assign OWNER role")

        if self.role == new_role:
            return self

        return replace(
            self,
            role=new_role,
            updated_at=now,
            updated_by_user_id=by_user_id,
        )

    def deactivate(
            self,
            *,
            actor_role: OrganizationRole,
            now: datetime,
            by_user_id: UUID,
    ) -> "OrganizationUser":

        if self.role == OrganizationRole.OWNER:
            raise PermissionDenied("Cannot deactivate OWNER")

        if self.role == self.role and not self.is_active:
            return self

        if actor_role != OrganizationRole.OWNER and self.role == OrganizationRole.ADMIN:
            raise PermissionDenied("Only OWNER can deactivate ADMIN")

        return replace(
            self,
            is_active=False,
            updated_at=now,
            updated_by_user_id=by_user_id,
        )

    def remove(
            self,
            *,
            actor_role: OrganizationRole,
            now: datetime,
            by_user_id: UUID,
    ) -> "OrganizationUser":

        if self.role == OrganizationRole.OWNER:
            raise PermissionDenied("Cannot remove OWNER")


        if actor_role != OrganizationRole.OWNER and self.role == OrganizationRole.ADMIN:
            raise PermissionDenied("Only OWNER can remove ADMIN")

        if not self.is_active:
            return self

        return replace(
            self,
            is_active=False,
            updated_at=now,
            updated_by_user_id=by_user_id,
        )