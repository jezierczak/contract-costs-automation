from uuid import UUID

from contract_costs.model.contract import Contract, ContractStatus
from contract_costs.repository.contract_repository import ContractRepository
from contract_costs.infrastructure.db.mysql_connection import get_connection


class MySQLContractRepository(ContractRepository):

    def add(self, contract: Contract) -> None:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO contract (
                id, code, name, description,
                owner_id, client_id,
                start_date, end_date,
                budget, path, status
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                str(contract.id),
                contract.code,
                contract.name,
                contract.description,
                str(contract.owner.id),
                str(contract.client.id),
                contract.start_date,
                contract.end_date,
                contract.budget,
                str(contract.path),
                contract.status.value,
            ),
        )

        conn.commit()
        cur.close()
        conn.close()

    def update(self, contract: Contract) -> None:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            UPDATE contract SET
                code=%s,
                name=%s,
                description=%s,
                owner_id=%s,
                client_id=%s,
                start_date=%s,
                end_date=%s,
                budget=%s,
                path=%s,
                status=%s
            WHERE id=%s
            """,
            (
                contract.code,
                contract.name,
                contract.description,
                str(contract.owner.id),
                str(contract.client.id),
                contract.start_date,
                contract.end_date,
                contract.budget,
                str(contract.path),
                contract.status.value,
                str(contract.id),
            ),
        )

        conn.commit()
        cur.close()
        conn.close()

    def get(self, contract_id: UUID) -> Contract | None:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute(
            "SELECT * FROM contract WHERE id = %s",
            (str(contract_id),),
        )
        row = cur.fetchone()

        cur.close()
        conn.close()

        return self._row_to_contract(row) if row else None

    def list(self) -> list[Contract]:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute("SELECT * FROM contract")
        rows = cur.fetchall()

        cur.close()
        conn.close()

        return [self._row_to_contract(row) for row in rows]

    def exists(self, contract_id: UUID) -> bool:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT 1 FROM contract WHERE id = %s LIMIT 1",
            (str(contract_id),),
        )

        exists = cur.fetchone() is not None

        cur.close()
        conn.close()

        return exists

    # ---------- helper ----------
    @staticmethod
    def _row_to_contract(row: dict) -> Contract:
        from contract_costs.repository.mysql.company_repository import (
            MySQLCompanyRepository,
        )

        company_repo = MySQLCompanyRepository()

        owner = company_repo.get(UUID(row["owner_id"]))
        client = company_repo.get(UUID(row["client_id"]))

        return Contract(
            id=UUID(row["id"]),
            code=row["code"],
            name=row["name"],
            description=row["description"],
            owner=owner,
            client=client,
            start_date=row["start_date"],
            end_date=row["end_date"],
            budget=row["budget"],
            path=row["path"],
            status=ContractStatus(row["status"]),
        )
