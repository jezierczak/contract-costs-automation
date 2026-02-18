import logging
from uuid import UUID

from contract_costs.infrastructure.db.mysql_connection import get_connection
from contract_costs.model.company import Address, BankAccount, Company, CompanyType, Contact
from contract_costs.repository.company_repository import CompanyRepository

logger = logging.getLogger(__name__)


class MySQLCompanyRepository(CompanyRepository):
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

    @staticmethod
    def _row_to_company(row: dict) -> Company:
        return Company(
            id=UUID(row["id"]),
            organization_id=UUID(row["organization_id"]),
            name=row["name"],
            description=row["description"],
            tax_number=row["tax_number"],
            address=Address(
                street=row["street"],
                city=row["city"],
                zip_code=row["zip_code"],
                country=row["country"],
            ),
            contact=Contact(
                phone_number=row["phone_number"],
                email=row["email"],
            ),
            bank_account=(
                BankAccount(
                    account_number=row["bank_account_number"],
                    country_code=row["bank_account_country_code"],
                )
                if row["bank_account_number"]
                else None
            ),
            role=CompanyType(row["role"]),
            tags=set(),
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
            created_by_user_id=(UUID(row["created_by_user_id"]) if row["created_by_user_id"] else None),
            updated_at=row["updated_at"],
            updated_by_user_id=(UUID(row["updated_by_user_id"]) if row["updated_by_user_id"] else None),
        )

    def add(self, company: Company) -> None:
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO companies (
                        id, organization_id, name, description, tax_number,
                        street, city, zip_code, country, phone_number, email,
                        bank_account_number, bank_account_country_code,
                        role, is_active, created_at, created_by_user_id
                    )
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """,
                    (
                        str(company.id),
                        str(company.organization_id),
                        company.name,
                        company.description,
                        company.tax_number,
                        company.address.street if company.address else None,
                        company.address.city if company.address else None,
                        company.address.zip_code if company.address else None,
                        company.address.country if company.address else None,
                        company.contact.phone_number if company.contact else None,
                        company.contact.email if company.contact else None,
                        company.bank_account.account_number if company.bank_account else None,
                        company.bank_account.country_code if company.bank_account else None,
                        company.role.value,
                        company.is_active,
                        company.created_at,
                        str(company.created_by_user_id) if company.created_by_user_id else None,
                    ),
                )
            self._maybe_commit(conn)
        except Exception:
            self._maybe_rollback(conn)
            raise
        finally:
            self._maybe_close(conn)

    def update(self, company: Company) -> None:
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE companies
                    SET name=%s, description=%s, tax_number=%s, street=%s, city=%s,
                        zip_code=%s, country=%s, phone_number=%s, email=%s,
                        bank_account_number=%s, bank_account_country_code=%s,
                        role=%s, is_active=%s, updated_at=%s, updated_by_user_id=%s
                    WHERE id = %s AND organization_id = %s
                    """,
                    (
                        company.name,
                        company.description,
                        company.tax_number,
                        company.address.street if company.address else None,
                        company.address.city if company.address else None,
                        company.address.zip_code if company.address else None,
                        company.address.country if company.address else None,
                        company.contact.phone_number if company.contact else None,
                        company.contact.email if company.contact else None,
                        company.bank_account.account_number if company.bank_account else None,
                        company.bank_account.country_code if company.bank_account else None,
                        company.role.value,
                        company.is_active,
                        company.updated_at,
                        str(company.updated_by_user_id) if company.updated_by_user_id else None,
                        str(company.id),
                        str(company.organization_id),
                    ),
                )
                if cur.rowcount == 0:
                    cur.execute(
                        "SELECT 1 FROM companies WHERE id=%s AND organization_id=%s",
                        (str(company.id), str(company.organization_id)),
                    )
                    if cur.fetchone() is None:
                        raise RuntimeError("Company not found or org mismatch")
                    logger.info("Company unchanged (no update needed)")
            self._maybe_commit(conn)
        except Exception:
            self._maybe_rollback(conn)
            raise
        finally:
            self._maybe_close(conn)

    def delete(self, company_id: UUID, organization_id: UUID) -> None:
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM companies WHERE id = %s and organization_id=%s LIMIT 1",
                    (str(company_id), str(organization_id)),
                )
            self._maybe_commit(conn)
        except Exception:
            self._maybe_rollback(conn)
            raise
        finally:
            self._maybe_close(conn)

    def get(self, company_id: UUID, organization_id: UUID) -> Company | None:
        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(
                    "SELECT * FROM companies WHERE id = %s and organization_id = %s",
                    (str(company_id), str(organization_id)),
                )
                row = cur.fetchone()
            return self._row_to_company(row) if row else None
        finally:
            self._maybe_close(conn)

    def list_all(self, organization_id: UUID) -> list[Company]:
        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute("SELECT * FROM companies where organization_id = %s", (str(organization_id),))
                rows = cur.fetchall()
            return [self._row_to_company(row) for row in rows]
        finally:
            self._maybe_close(conn)

    def exists(self, company_id: UUID, organization_id: UUID) -> bool:
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT 1 FROM companies WHERE id = %s and organization_id = %s LIMIT 1",
                    (str(company_id), str(organization_id)),
                )
                return cur.fetchone() is not None
        finally:
            self._maybe_close(conn)

    def get_by_tax_number(self, tax_number: str, organization_id: UUID) -> Company | None:
        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(
                    "SELECT * FROM companies WHERE tax_number = %s and organization_id = %s",
                    (tax_number, str(organization_id)),
                )
                row = cur.fetchone()
            return self._row_to_company(row) if row else None
        finally:
            self._maybe_close(conn)

    def get_owners(self, organization_id: UUID) -> list[Company]:
        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(
                    """
                    SELECT *
                    FROM companies
                    WHERE role = %s AND is_active = 1 AND organization_id = %s
                    """,
                    (CompanyType.OWN.value, str(organization_id)),
                )
                rows = cur.fetchall()
            return [self._row_to_company(row) for row in rows]
        finally:
            self._maybe_close(conn)

    def exists_owner(self, organization_id: UUID) -> bool:
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT 1 FROM companies WHERE role = %s AND is_active = 1 and organization_id = %s LIMIT 1",
                    (CompanyType.OWN.value, str(organization_id)),
                )
                return cur.fetchone() is not None
        finally:
            self._maybe_close(conn)

    def find_by_bank_account(self, organization_id: UUID, bank_account_number: str) -> list[Company]:
        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(
                    "SELECT * FROM companies WHERE bank_account_number = %s and organization_id = %s",
                    (bank_account_number, str(organization_id)),
                )
                rows = cur.fetchall()
            return [self._row_to_company(row) for row in rows]
        finally:
            self._maybe_close(conn)

    def find_by_email(self, organization_id: UUID, email: str) -> list[Company]:
        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(
                    "SELECT * FROM companies WHERE email = %s and organization_id = %s",
                    (email, str(organization_id)),
                )
                rows = cur.fetchall()
            return [self._row_to_company(row) for row in rows]
        finally:
            self._maybe_close(conn)

    def find_by_phone(self, organization_id: UUID, phone_number: str) -> list[Company]:
        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(
                    "SELECT * FROM companies WHERE phone_number = %s and organization_id = %s",
                    (phone_number, str(organization_id)),
                )
                rows = cur.fetchall()
            return [self._row_to_company(row) for row in rows]
        finally:
            self._maybe_close(conn)

    def find_by_name_like(self, organization_id: UUID, name: str) -> list[Company]:
        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(
                    "SELECT * FROM companies WHERE name LIKE %s and organization_id = %s",
                    (f"%{name}%", str(organization_id)),
                )
                rows = cur.fetchall()
            return [self._row_to_company(row) for row in rows]
        finally:
            self._maybe_close(conn)

    def find_by_street_tokens(self, organization_id: UUID, tokens: list[str]) -> list[Company]:
        if not tokens:
            return []

        where_clauses = []
        params = [str(organization_id)]
        for token in tokens:
            where_clauses.append("LOWER(street) LIKE %s")
            params.append(f"%{token.lower()}%")

        sql = f"""
            SELECT *
            FROM companies
            WHERE street IS NOT NULL and organization_id = %s
              AND {' AND '.join(where_clauses)}
        """

        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql, params)
                rows = cur.fetchall()
            return [self._row_to_company(row) for row in rows]
        finally:
            self._maybe_close(conn)
