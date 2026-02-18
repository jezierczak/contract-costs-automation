from uuid import UUID

from contract_costs.model.contract import Contract, ContractStatus, ContractType
from contract_costs.repository.contract_repository import ContractRepository
from contract_costs.infrastructure.db.mysql_connection import get_connection


class MySQLContractRepository(ContractRepository):
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

    def add(self, contract: Contract) -> None:
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO contracts (
                        id,
                        organization_id,
                        code,
                        name,
                        description,
                        owner_id,
                        client_id,
                        start_date,
                        end_date,
                        budget,
                        path,
                        status,
                        created_at,
                        created_by_user_id,
                        updated_at,
                        updated_by_user_id,
                        contract_type
                    )
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """,
                    (
                        str(contract.id),
                        str(contract.organization_id),
                        contract.code,
                        contract.name,
                        contract.description,
                        str(contract.owner.id),
                        str(contract.client.id) if contract.client else None,
                        contract.start_date,
                        contract.end_date,
                        contract.budget,
                        str(contract.path),
                        contract.status.value,
                        contract.created_at,
                        str(contract.created_by_user_id)
                        if contract.created_by_user_id
                        else None,
                        contract.updated_at,
                        str(contract.updated_by_user_id)
                        if contract.updated_by_user_id
                        else None,
                        contract.contract_type.value,
                    ),
                )
            self._maybe_commit(conn)
        except Exception:
            self._maybe_rollback(conn)
            raise
        finally:
            self._maybe_close(conn)

    def update(self, contract: Contract) -> None:
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE contracts SET
                        code=%s,
                        name=%s,
                        description=%s,
                        owner_id=%s,
                        client_id=%s,
                        start_date=%s,
                        end_date=%s,
                        budget=%s,
                        path=%s,
                        status=%s,
                        updated_at=%s,
                        updated_by_user_id=%s,
                        contract_type=%s
                    WHERE id=%s
                      AND organization_id=%s
                    """,
                    (
                        contract.code,
                        contract.name,
                        contract.description,
                        str(contract.owner.id),
                        str(contract.client.id) if contract.client else None,
                        contract.start_date,
                        contract.end_date,
                        contract.budget,
                        str(contract.path),
                        contract.status.value,
                        contract.updated_at,
                        str(contract.updated_by_user_id)
                        if contract.updated_by_user_id
                        else None,
                        contract.contract_type.value,
                        str(contract.id),
                        str(contract.organization_id),
                    ),
                )
            self._maybe_commit(conn)
        except Exception:
            self._maybe_rollback(conn)
            raise
        finally:
            self._maybe_close(conn)

    def get(
        self,
        *,
        organization_id: UUID,
        contract_id: UUID,
    ) -> Contract | None:
        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(
                    """
                    SELECT * FROM contracts
                    WHERE id = %s
                      AND organization_id = %s
                    """,
                    (str(contract_id), str(organization_id)),
                )
                row = cur.fetchone()
        finally:
            self._maybe_close(conn)

        return self._row_to_contract(row) if row else None

    def get_system_contract(
            self,
            organization_id: UUID,
            owner_id: UUID,
    ) -> Contract | None:

        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(
                    """
                    SELECT *
                    FROM contracts
                    WHERE organization_id = %s
                      AND contract_type = %s
                      AND owner_id = %s
                    LIMIT 1
                    """,
                    (
                        str(organization_id),
                        ContractType.SYSTEM.value,
                        str(owner_id),
                    ),
                )
                row = cur.fetchone()
        finally:
            self._maybe_close(conn)

        if not row:
            return None

        return self._row_to_contract(row)


    def list_contracts(self, organization_id: UUID,contract_type: ContractType = ContractType.PROJECT) -> list[Contract]:
        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(
                    """
                    SELECT * FROM contracts
                    WHERE organization_id = %s and contract_type = %s
                    """,
                    (str(organization_id),contract_type.value),
                )
                rows = cur.fetchall()
        finally:
            self._maybe_close(conn)

        return [self._row_to_contract(row) for row in rows]

    def exists(self, organization_id: UUID, contract_id: UUID) -> bool:
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 1 FROM contracts
                    WHERE id = %s
                      AND organization_id = %s
                    LIMIT 1
                    """,
                    (str(contract_id), str(organization_id)),
                )
                exists = cur.fetchone() is not None
        finally:
            self._maybe_close(conn)

        return exists

    def get_by_code(
            self,
            organization_id: UUID,
            contract_code: str,
    ) -> Contract | None:
        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(
                    """
                    SELECT *
                    FROM contracts
                    WHERE code = %s
                      AND organization_id = %s
                    """,
                    (contract_code, str(organization_id)),
                )
                row = cur.fetchone()
        finally:
            self._maybe_close(conn)

        return self._row_to_contract(row) if row else None

    # ---------- helper ----------

    def _row_to_contract(self,row: dict) -> Contract:
        from contract_costs.repository.mysql.company_repository import (
            MySQLCompanyRepository,
        )

        company_repo = MySQLCompanyRepository(connection=self._connection)
        organization_id = UUID(row["organization_id"])

        owner = company_repo.get(
            organization_id=organization_id,
            company_id=UUID(row["owner_id"]),
        )

        client = (
            company_repo.get(
                organization_id=organization_id,
                company_id=UUID(row["client_id"]),
            )
            if row["client_id"]
            else None
        )

        if not owner:
            raise RuntimeError(
                f"Owner not found in database for contract {row['code']}"
            )

        return Contract(
            id=UUID(row["id"]),
            organization_id=UUID(row["organization_id"]),
            created_at=row["created_at"],
            created_by_user_id=(
                UUID(row["created_by_user_id"])
                if row["created_by_user_id"]
                else None
            ),
            updated_at=row["updated_at"],
            updated_by_user_id=(
                UUID(row["updated_by_user_id"])
                if row["updated_by_user_id"]
                else None
            ),
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
            contract_type=ContractType(row["contract_type"]),
        )
