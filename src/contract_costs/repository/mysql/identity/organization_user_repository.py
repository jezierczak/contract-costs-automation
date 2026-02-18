from uuid import UUID

from contract_costs.infrastructure.db.mysql_connection import get_connection
from contract_costs.model.identity.organization_role import OrganizationRole
from contract_costs.model.identity.organization_user import OrganizationUser
from contract_costs.repository.identity.organization_user_repository import OrganizationUserRepository
from contract_costs.services.identity.query.dto.organization_list_item_dto import OrganizationListItemDTO
from contract_costs.services.identity.query.dto.organization_user_view import OrganizationUserView


class MySqlOrganizationUserRepository(OrganizationUserRepository):
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

    def add(self, organization_user: OrganizationUser) -> None:
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO organization_users (id, organization_id, user_id, role, is_active,
                                                    created_at, created_by_user_id, updated_at,
                                                    updated_by_user_id, invited_at, invited_by_user_id,
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
                        organization_user.created_at,
                        str(organization_user.updated_by_user_id) if organization_user.updated_by_user_id else None,
                        organization_user.invited_at,
                        str(organization_user.invited_by_user_id) if organization_user.invited_by_user_id else None,
                        organization_user.accepted_at,
                    ),
                )
            self._maybe_commit(conn)
        except Exception:
            self._maybe_rollback(conn)
            raise
        finally:
            self._maybe_close(conn)

    def update(self, organization_user: OrganizationUser) -> None:
        conn = self._get_connection()
        try:
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
                    ),
                )
            self._maybe_commit(conn)
        except Exception:
            self._maybe_rollback(conn)
            raise
        finally:
            self._maybe_close(conn)

    def get(self, organization_user_id: UUID) -> OrganizationUser | None:
        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute("SELECT * FROM organization_users WHERE id = %s", (str(organization_user_id),))
                row = cur.fetchone()
            return self._map_row(row) if row else None
        finally:
            self._maybe_close(conn)

    def get_by_org_and_user(self, *, organization_id: UUID, user_id: UUID) -> OrganizationUser | None:
        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(
                    """
                    SELECT *
                    FROM organization_users
                    WHERE organization_id = %s
                      AND user_id = %s
                    """,
                    (str(organization_id), str(user_id)),
                )
                row = cur.fetchone()
            return self._map_row(row) if row else None
        finally:
            self._maybe_close(conn)

    def list_by_organization(self, organization_id: UUID, *, active_only: bool = False) -> list[OrganizationUser]:
        sql = "SELECT * FROM organization_users WHERE organization_id = %s"
        params = [str(organization_id)]
        if active_only:
            sql += " AND is_active = TRUE"

        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql, params)
                rows = cur.fetchall()
            return [self._map_row(r) for r in rows]
        finally:
            self._maybe_close(conn)

    def list_by_user(self, user_id: UUID, *, active_only: bool = False) -> list[OrganizationUser]:
        sql = "SELECT * FROM organization_users WHERE user_id = %s"
        params = [str(user_id)]
        if active_only:
            sql += " AND is_active = TRUE"

        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql, params)
                rows = cur.fetchall()
            return [self._map_row(r) for r in rows]
        finally:
            self._maybe_close(conn)

    def exists(self, *, organization_id: UUID, user_id: UUID) -> bool:
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 1
                    FROM organization_users
                    WHERE organization_id = %s
                      AND user_id = %s
                    LIMIT 1
                    """,
                    (str(organization_id), str(user_id)),
                )
                return cur.fetchone() is not None
        finally:
            self._maybe_close(conn)

    def list_organizations_for_user(
            self,
            *,
            user_id: UUID,
            active_only: bool = True,
    ) -> list[OrganizationListItemDTO]:

        sql = """
              SELECT o.id, 
                     o.code, 
                     o.name, 
                     o.is_active, 
                     m.role
              FROM organization_users m
                       JOIN organizations o ON o.id = m.organization_id
              WHERE m.user_id = %s 
              """

        params = [str(user_id)]

        if active_only:
            sql += " AND m.is_active = TRUE AND o.is_active = TRUE"

        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql, params)
                rows = cur.fetchall()

            return [
                OrganizationListItemDTO(
                    id=UUID(row["id"]),
                    code=row["code"],
                    name=row["name"],
                    is_active=bool(row["is_active"]),
                    role=row["role"],  # jeśli DTO trzyma string
                )
                for row in rows
            ]
        finally:
            self._maybe_close(conn)

    def list_users_for_organization(
            self,
            *,
            organization_id: UUID,
            active_only: bool = False,
    ) -> list[OrganizationUserView]:

        sql = """
              SELECT u.id, 
                     u.login, 
                     u.full_name, 
                     u.email, 
                     m.role, 
                     m.is_active, 
                     m.invited_at, 
                     m.accepted_at
              FROM organization_users m
                       JOIN users u ON u.id = m.user_id
              WHERE m.organization_id = %s 
              """

        params = [str(organization_id)]

        if active_only:
            sql += " AND m.is_active = TRUE"

        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql, params)
                rows = cur.fetchall()

            return [
                OrganizationUserView(
                    user_id=UUID(r["id"]),
                    login=r["login"],
                    full_name=r["full_name"],
                    email=r["email"],
                    role=r["role"],
                    is_active=r["is_active"],
                    invited_at=r["invited_at"],
                    accepted_at=r["accepted_at"],
                )
                for r in rows
            ]
        finally:
            self._maybe_close(conn)

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
