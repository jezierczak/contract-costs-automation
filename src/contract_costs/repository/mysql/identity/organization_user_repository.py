from uuid import UUID

from contract_costs.infrastructure.db.mysql_connection import get_connection
from contract_costs.model.identity.organization_role import OrganizationRole
from contract_costs.model.identity.organization_user import OrganizationUser
from contract_costs.repository.identity.organization_user_repository import OrganizationUserRepository


class MySqlOrganizationUserRepository(OrganizationUserRepository):

    def add(self, organization_user: OrganizationUser) -> None:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO organization_users (id,
                                                organization_id,
                                                user_id,
                                                role,
                                                is_active,
                                                created_at,
                                                created_by_user_id,
                                                updated_at,
                                                updated_by_user_id,
                                                invited_at,
                                                invited_by_user_id,
                                                accepted_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    str(organization_user.id),
                    str(organization_user.organization_id),
                    str(organization_user.user_id),
                    organization_user.role.value,
                    organization_user.is_active,
                    organization_user.created_at,
                    str(organization_user.created_by_user_id) if organization_user.created_by_user_id else None,
                    organization_user.created_at,  # updated_at = created_at
                    str(organization_user.updated_by_user_id) if organization_user.updated_by_user_id else None,
                    organization_user.invited_at,
                    str(organization_user.invited_by_user_id) if organization_user.invited_by_user_id else None,
                    organization_user.accepted_at,
                )
            )
        conn.commit()

    def update(self, organization_user: OrganizationUser) -> None:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE organization_users
                SET role               = %s,
                    is_active          = %s,
                    updated_at         = %s,
                    updated_by_user_id = %s,
                    invited_at         = %s,
                    invited_by_user_id = %s,
                    accepted_at        = %s
                WHERE id = %s
                """,
                (
                    organization_user.role.value,
                    organization_user.is_active,
                    organization_user.updated_at,
                    str(organization_user.updated_by_user_id) if organization_user.updated_by_user_id else None,
                    organization_user.invited_at,
                    str(organization_user.invited_by_user_id) if organization_user.invited_by_user_id else None,
                    organization_user.accepted_at,
                    str(organization_user.id),
                )
            )
        conn.commit()

    def get(self, organization_user_id: UUID) -> OrganizationUser | None:
        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(
                "SELECT * FROM organization_users WHERE id = %s",
                (str(organization_user_id),)
            )
            row = cur.fetchone()
        return self._map_row(row) if row else None

    def get_by_org_and_user(
            self,
            *,
            organization_id: UUID,
            user_id: UUID,
    ) -> OrganizationUser | None:
        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(
                """
                SELECT *
                FROM organization_users
                WHERE organization_id = %s
                  AND user_id = %s
                """,
                (str(organization_id), str(user_id))
            )
            row = cur.fetchone()
        return self._map_row(row) if row else None

    def list_by_organization(
            self,
            organization_id: UUID,
            *,
            active_only: bool = False,
    ) -> list[OrganizationUser]:
        sql = "SELECT * FROM organization_users WHERE organization_id = %s"
        params = [str(organization_id)]

        if active_only:
            sql += " AND is_active = TRUE"

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()

        return [self._map_row(r) for r in rows]

    def list_by_user(
            self,
            user_id: UUID,
            *,
            active_only: bool = False,
    ) -> list[OrganizationUser]:
        sql = "SELECT * FROM organization_users WHERE user_id = %s"
        params = [str(user_id)]

        if active_only:
            sql += " AND is_active = TRUE"

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()

        return [self._map_row(r) for r in rows]

    def exists(
            self,
            *,
            organization_id: UUID,
            user_id: UUID,
    ) -> bool:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT 1
                FROM organization_users
                WHERE organization_id = %s
                  AND user_id = %s
                LIMIT 1
                """,
                (str(organization_id), str(user_id))
            )
            return cur.fetchone() is not None

    @staticmethod
    def _map_row(row: dict) -> OrganizationUser:
        return OrganizationUser(
            id=UUID(row["id"]),
            organization_id=UUID(row["organization_id"]),
            user_id=UUID(row["user_id"]),
            role=OrganizationRole(row["role"]),
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
            created_by_user_id=UUID(row["created_by_user_id"]) if row["created_by_user_id"] else None,
            updated_at=row["updated_at"],
            updated_by_user_id=UUID(row["updated_by_user_id"]) if row["updated_by_user_id"] else None,
            invited_at=row["invited_at"],
            invited_by_user_id=UUID(row["invited_by_user_id"]) if row["invited_by_user_id"] else None,
            accepted_at=row["accepted_at"],
        )