from uuid import UUID

from contract_costs.infrastructure.db.mysql_connection import get_connection
from contract_costs.model.company_ksef_settings import CompanyKsefSettings, KsefEnvironment
from contract_costs.repository.company_ksef_settings_repository import CompanyKsefSettingsRepository


class MySQLCompanyKsefSettingsRepository(CompanyKsefSettingsRepository):
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

    def get_by_company_id(
        self,
        *,
        organization_id: UUID,
        company_id: UUID,
    ) -> CompanyKsefSettings | None:
        sql = """
        SELECT *
        FROM company_ksef_settings
        WHERE organization_id = %s
          AND company_id = %s
        LIMIT 1
        """

        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql, (str(organization_id), str(company_id)))
                row = cur.fetchone()
            return self._map_row(row) if row else None
        finally:
            self._maybe_close(conn)

    def add(
        self,
        *,
        organization_id: UUID,
        settings: CompanyKsefSettings,
    ) -> None:
        sql = """
        INSERT INTO company_ksef_settings (
            id, organization_id, company_id, environment, is_enabled,
            certificate_path, certificate_password, last_import_from,
            last_import_at, last_error, created_at, created_by_user_id,
            updated_at, updated_by_user_id
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    sql,
                    (
                        str(settings.id),
                        str(organization_id),
                        str(settings.company_id),
                        settings.environment.value,
                        settings.is_enabled,
                        settings.certificate_path,
                        settings.certificate_password,
                        settings.last_import_from,
                        settings.last_import_at,
                        settings.last_error,
                        settings.created_at,
                        str(settings.created_by_user_id) if settings.created_by_user_id else None,
                        settings.updated_at,
                        str(settings.updated_by_user_id) if settings.updated_by_user_id else None,
                    ),
                )
            self._maybe_commit(conn)
        except Exception:
            self._maybe_rollback(conn)
            raise
        finally:
            self._maybe_close(conn)

    def update(
        self,
        *,
        organization_id: UUID,
        settings: CompanyKsefSettings,
    ) -> None:
        sql = """
        UPDATE company_ksef_settings
        SET environment = %s,
            is_enabled = %s,
            certificate_path = %s,
            certificate_password = %s,
            last_import_from = %s,
            last_import_at = %s,
            last_error = %s,
            updated_at = %s,
            updated_by_user_id = %s
        WHERE organization_id = %s
          AND company_id = %s
        """

        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    sql,
                    (
                        settings.environment.value,
                        settings.is_enabled,
                        settings.certificate_path,
                        settings.certificate_password,
                        settings.last_import_from,
                        settings.last_import_at,
                        settings.last_error,
                        settings.updated_at,
                        str(settings.updated_by_user_id) if settings.updated_by_user_id else None,
                        str(organization_id),
                        str(settings.company_id),
                    ),
                )
            self._maybe_commit(conn)
        except Exception:
            self._maybe_rollback(conn)
            raise
        finally:
            self._maybe_close(conn)

    @staticmethod
    def _map_row(row: dict) -> CompanyKsefSettings:
        return CompanyKsefSettings(
            id=UUID(row["id"]),
            organization_id=UUID(row["organization_id"]),
            company_id=UUID(row["company_id"]),
            environment=KsefEnvironment(row["environment"]),
            is_enabled=bool(row["is_enabled"]),
            certificate_path=row["certificate_path"],
            certificate_password=row["certificate_password"],
            last_import_from=row["last_import_from"],
            last_import_at=row["last_import_at"],
            last_error=row["last_error"],
            created_at=row["created_at"],
            created_by_user_id=UUID(row["created_by_user_id"]) if row["created_by_user_id"] else None,
            updated_at=row["updated_at"],
            updated_by_user_id=UUID(row["updated_by_user_id"]) if row["updated_by_user_id"] else None,
        )
