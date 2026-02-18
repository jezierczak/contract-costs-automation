import json
from uuid import UUID

from contract_costs.infrastructure.db.mysql_connection import get_connection
from contract_costs.model.identity.organization import Organization
from contract_costs.model.identity.organization_user import OrganizationUser
from contract_costs.model.identity.user import User
from contract_costs.repository.identity.organization_repository import OrganizationRepository


class MySqlOrganizationRepository(OrganizationRepository):
    def __init__(self, connection=None) -> None:
        self._connection = connection

    def _get_connection(self):
        return self._connection or get_connection()

    def _maybe_commit(self, conn) -> None:
        if self._connection is None:
            conn.commit()

    def _maybe_rollback(self, conn) -> None:
        if self._connection is None:
            conn.rollback()

    def _maybe_close(self, conn) -> None:
        if self._connection is None:
            conn.close()

    def add_with_owner(self, *, organization: Organization, owner: User, membership: OrganizationUser) -> None:
        conn = self._get_connection()
        try:
            if self._connection is None:
                conn.start_transaction()

            with conn.cursor() as cur:
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
                        str(organization.created_by_user_id) if organization.created_by_user_id else None,
                        json.dumps(organization.settings) if organization.settings else None,
                    ),
                )

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
                        str(owner.created_by_user_id) if owner.created_by_user_id else None,
                    ),
                )

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
                        str(membership.created_by_user_id) if membership.created_by_user_id else None,
                    ),
                )

            self._maybe_commit(conn)
        except Exception:
            self._maybe_rollback(conn)
            raise
        finally:
            self._maybe_close(conn)

    def add(self, organization: Organization) -> None:
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO organizations (id, code, name, is_active, created_at,
                                               created_by_user_id, updated_at,
                                               updated_by_user_id, settings)
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
                    ),
                )
            self._maybe_commit(conn)
        except Exception:
            self._maybe_rollback(conn)
            raise
        finally:
            self._maybe_close(conn)

    def update(self, organization: Organization) -> None:
        conn = self._get_connection()
        try:
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
                    ),
                )
            self._maybe_commit(conn)
        except Exception:
            self._maybe_rollback(conn)
            raise
        finally:
            self._maybe_close(conn)

    def get(self, organization_id: UUID) -> Organization | None:
        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute("SELECT * FROM organizations WHERE id = %s", (str(organization_id),))
                row = cur.fetchone()
            return self._map_row(row) if row else None
        finally:
            self._maybe_close(conn)

    def get_by_code(self, code: str) -> Organization | None:
        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute("SELECT * FROM organizations WHERE code = %s", (code,))
                row = cur.fetchone()
            return self._map_row(row) if row else None
        finally:
            self._maybe_close(conn)

    def list(self, *, active_only: bool = False) -> list[Organization]:
        sql = "SELECT * FROM organizations"
        if active_only:
            sql += " WHERE is_active = TRUE"

        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql)
                rows = cur.fetchall()
            return [self._map_row(r) for r in rows]
        finally:
            self._maybe_close(conn)

    def exists(self, organization_id: UUID) -> bool:
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM organizations WHERE id = %s LIMIT 1", (str(organization_id),))
                return cur.fetchone() is not None
        finally:
            self._maybe_close(conn)

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
