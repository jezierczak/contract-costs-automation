from typing import Iterable
from uuid import UUID

from contract_costs.model.company import Company, CompanyType
from contract_costs.model.company import Address, BankAccount, Contact
from contract_costs.repository.company_repository import CompanyRepository
from contract_costs.infrastructure.db.mysql_connection import get_connection


class MySQLCompanyRepository(CompanyRepository):

    # ---------- helpers ----------

    @staticmethod
    def _row_to_company(row: dict) -> Company:
        return Company(
            id=UUID(row["id"]),
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
                    number=row["bank_account_number"],
                    country_code=row["bank_account_country_code"],
                )
                if row["bank_account_number"]
                else None
            ),
            role=CompanyType(row["role"]),
            tags=set(),  # TODO
            is_active=bool(row["is_active"]),
        )

    # ---------- CRUD ----------

    def add(self, company: Company) -> None:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO companies (
                id, name, description, tax_number,
                street, city, zip_code, country,
                phone_number, email,
                bank_account_number, bank_account_country_code,
                role, is_active
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                str(company.id),
                company.name,
                company.description,
                company.tax_number,
                company.address.street if company.address else None,
                company.address.city if company.address else None,
                company.address.zip_code if company.address else None,
                company.address.country if company.address else None,
                company.contact.phone_number if company.contact else None,
                company.contact.email if company.contact else None,
                company.bank_account.number if company.bank_account else None,
                company.bank_account.country_code if company.bank_account else None,
                company.role.value,
                company.is_active,
            ),
        )

        conn.commit()
        cur.close()
        conn.close()

    def update(self, company: Company) -> None:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            UPDATE companies SET
                name=%s,
                description=%s,
                tax_number=%s,
                street=%s,
                city=%s,
                zip_code=%s,
                country=%s,
                phone_number=%s,
                email=%s,
                bank_account_number=%s,
                bank_account_country_code=%s,
                role=%s,
                is_active=%s
            WHERE id=%s
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
                company.bank_account.number if company.bank_account else None,
                company.bank_account.country_code if company.bank_account else None,
                company.role.value,
                company.is_active,
                str(company.id),
            ),
        )

        conn.commit()
        cur.close()
        conn.close()

    def delete(self, company_id: UUID) -> None:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "DELETE FROM companies WHERE id = %s LIMIT 1",
            (str(company_id),),
        )

        conn.commit()
        cur.close()
        conn.close()

    def get(self, company_id: UUID) -> Company | None:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute(
            "SELECT * FROM companies WHERE id = %s",
            (str(company_id),),
        )

        row = cur.fetchone()
        cur.close()
        conn.close()

        return self._row_to_company(row) if row else None

    def list_all(self) -> list[Company]:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute("SELECT * FROM companies")
        rows = cur.fetchall()

        cur.close()
        conn.close()

        return [self._row_to_company(row) for row in rows]

    def exists(self, company_id: UUID) -> bool:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT 1 FROM companies WHERE id = %s LIMIT 1",
            (str(company_id),),
        )

        exists = cur.fetchone() is not None
        cur.close()
        conn.close()

        return exists

    # ---------- identity ----------

    def get_by_tax_number(self, tax_number: str) -> Company | None:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute(
            "SELECT * FROM companies WHERE tax_number = %s",
            (tax_number,),
        )

        row = cur.fetchone()
        cur.close()
        conn.close()

        return self._row_to_company(row) if row else None

    def get_owners(self) -> list[Company]:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute(
            "SELECT * FROM companies WHERE role = %s AND is_active = 1",
            (CompanyType.OWN.value,),
        )

        rows = cur.fetchall()
        cur.close()
        conn.close()

        return [self._row_to_company(row) for row in rows]

    def exists_owner(self) -> bool:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT 1 FROM companies WHERE role = %s AND is_active = 1 LIMIT 1",
            (CompanyType.OWN.value,),
        )

        exists = cur.fetchone() is not None
        cur.close()
        conn.close()

        return exists

    # ---------- candidate search ----------

    def find_by_bank_account(self, bank_account: str) -> list[Company]:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute(
            "SELECT * FROM companies WHERE bank_account_number = %s",
            (bank_account,),
        )

        rows = cur.fetchall()
        cur.close()
        conn.close()

        return [self._row_to_company(row) for row in rows]

    def find_by_email(self, email: str) -> list[Company]:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute(
            "SELECT * FROM companies WHERE email = %s",
            (email,),
        )

        rows = cur.fetchall()
        cur.close()
        conn.close()

        return [self._row_to_company(row) for row in rows]

    def find_by_phone(self, phone_number: str) -> list[Company]:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute(
            "SELECT * FROM companies WHERE phone_number = %s",
            (phone_number,),
        )

        rows = cur.fetchall()
        cur.close()
        conn.close()

        return [self._row_to_company(row) for row in rows]

    def find_by_name_like(self, name: str) -> list[Company]:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute(
            "SELECT * FROM companies WHERE name LIKE %s",
            (f"%{name}%",),
        )

        rows = cur.fetchall()
        cur.close()
        conn.close()

        return [self._row_to_company(row) for row in rows]

    def find_by_street_tokens(self, tokens: list[str]) -> list[Company]:
        if not tokens:
            return []

        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        where_clauses = []
        params = []

        for token in tokens:
            where_clauses.append("LOWER(street) LIKE %s")
            params.append(f"%{token.lower()}%")

        sql = f"""
            SELECT *
            FROM companies
            WHERE street IS NOT NULL
              AND {' AND '.join(where_clauses)}
        """

        cur.execute(sql, params)
        rows = cur.fetchall()

        cur.close()
        conn.close()

        return [self._row_to_company(row) for row in rows]