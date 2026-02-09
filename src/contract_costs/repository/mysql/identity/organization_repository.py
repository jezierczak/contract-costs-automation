import json
from uuid import UUID

from contract_costs.model.identity.organization import Organization
from contract_costs.model.identity.organization_user import OrganizationUser
from contract_costs.model.identity.user import User
from contract_costs.repository.identity.organization_repository import OrganizationRepository
from contract_costs.infrastructure.db.mysql_connection import get_connection


class MySqlOrganizationRepository(OrganizationRepository):

    def add_with_owner(
            self,
            *,
            organization: Organization,
            owner: User,
            membership: OrganizationUser,
    ) -> None:
        conn = get_connection()
        try:
            conn.start_transaction()

            with conn.cursor() as cur:
                # --- organization ---
                cur.execute(
                    """
                    INSERT INTO organizations (id, code, name, is_active,
                                               created_at, created_by_user_id, settings)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        str(organization.id),
                        organization.code,
                        organization.name,
                        organization.is_active,
                        organization.created_at,
                        str(organization.created_by_user_id)
                        if organization.created_by_user_id else None,
                        organization.settings,
                    ),
                )

                # --- user ---
                cur.execute(
                    """
                    INSERT INTO users (id, login, email, full_name,
                                       is_active, created_at, created_by_user_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        str(owner.id),
                        owner.login,
                        owner.email,
                        owner.full_name,
                        owner.is_active,
                        owner.created_at,
                        str(owner.created_by_user_id)
                        if owner.created_by_user_id else None,
                    ),
                )

                # --- organization_user ---
                cur.execute(
                    """
                    INSERT INTO organization_users (id,
                                                    organization_id,
                                                    user_id,
                                                    role,
                                                    is_active,
                                                    invited_at,
                                                    accepted_at,
                                                    created_at,
                                                    created_by_user_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        str(membership.id),
                        str(membership.organization_id),
                        str(membership.user_id),
                        membership.role.value,
                        membership.is_active,
                        membership.invited_at,
                        membership.accepted_at,
                        membership.created_at,
                        str(membership.created_by_user_id)
                        if membership.created_by_user_id else None,
                    ),
                )

            conn.commit()

        except Exception:
            conn.rollback()
            raise

    def add(self, organization: Organization) -> None:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO organizations (id,
                                           code,
                                           name,
                                           is_active,
                                           created_at,
                                           created_by_user_id,
                                           updated_at,
                                           updated_by_user_id,
                                           settings)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    str(organization.id),
                    organization.code,
                    organization.name,
                    organization.is_active,
                    organization.created_at,
                    str(organization.created_by_user_id) if organization.created_by_user_id else None,
                    organization.updated_at,
                    str(organization.updated_by_user_id) if organization.updated_by_user_id else None,
                    json.dumps(organization.settings) if organization.settings else None,
                )
            )
        conn.commit()

    def update(self, organization: Organization) -> None:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE organizations
                SET code               = %s,
                    name               = %s,
                    is_active          = %s,
                    updated_at         = %s,
                    updated_by_user_id = %s,
                    settings           = %s
                WHERE id = %s
                """,
                (
                    organization.code,
                    organization.name,
                    organization.is_active,
                    organization.updated_at,
                    str(organization.updated_by_user_id) if organization.updated_by_user_id else None,
                    json.dumps(organization.settings) if organization.settings else None,
                    str(organization.id),
                )
            )
        conn.commit()

    def get(self, organization_id: UUID) -> Organization | None:
        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(
                "SELECT * FROM organizations WHERE id = %s",
                (str(organization_id),)
            )
            row = cur.fetchone()
        return self._map_row(row) if row else None

    def get_by_code(self, code: str) -> Organization | None:
        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(
                "SELECT * FROM organizations WHERE code = %s",
                (code,)
            )
            row = cur.fetchone()
        return self._map_row(row) if row else None

    def list(self, *, active_only: bool = False) -> list[Organization]:
        sql = "SELECT * FROM organizations"
        params: tuple = ()

        if active_only:
            sql += " WHERE is_active = TRUE"

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()

        return [self._map_row(r) for r in rows]

    def exists(self, organization_id: UUID) -> bool:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM organizations WHERE id = %s LIMIT 1",
                (str(organization_id),)
            )
            return cur.fetchone() is not None

    @staticmethod
    def _map_row(row: dict) -> Organization:
        return Organization(
            id=UUID(row["id"]),
            code=row["code"],
            name=row["name"],
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
            created_by_user_id=UUID(row["created_by_user_id"]) if row["created_by_user_id"] else None,
            updated_at=row["updated_at"],
            updated_by_user_id=UUID(row["updated_by_user_id"]) if row["updated_by_user_id"] else None,
            settings=json.loads(row["settings"]) if row.get("settings") else None,
        )
