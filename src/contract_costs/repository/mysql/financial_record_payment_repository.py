from decimal import Decimal
from uuid import UUID

from contract_costs.infrastructure.db.mysql_connection import get_connection
from contract_costs.model.financial_record_payment import FinancialRecordPayment
from contract_costs.repository.financial_record_payment_repository import (
    FinancialRecordPaymentRepository,
)


class MySQLFinancialRecordPaymentRepository(FinancialRecordPaymentRepository):
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

    def add(self, *, organization_id: UUID, payment: FinancialRecordPayment) -> None:
        sql = """
        INSERT INTO financial_record_payments (
            id, organization_id, financial_record_id, amount, paid_date,
            created_at, created_by_user_id, updated_at, updated_by_user_id
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    sql,
                    (
                        str(payment.id),
                        str(organization_id),
                        str(payment.financial_record_id),
                        payment.amount,
                        payment.paid_date,
                        payment.created_at,
                        str(payment.created_by_user_id) if payment.created_by_user_id else None,
                        payment.updated_at,
                        str(payment.updated_by_user_id) if payment.updated_by_user_id else None,
                    ),
                )
            self._maybe_commit(conn)
        except Exception:
            self._maybe_rollback(conn)
            raise
        finally:
            self._maybe_close(conn)

    def get(self, *, organization_id: UUID, payment_id: UUID) -> FinancialRecordPayment | None:
        sql = """
              SELECT *
              FROM financial_record_payments
              WHERE id = %s
                AND organization_id = %s
              """

        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql, (str(payment_id), str(organization_id)))
                row = cur.fetchone()
            return self._map_row(row) if row else None
        finally:
            self._maybe_close(conn)

    def list_by_financial_record(
        self, *, organization_id: UUID, financial_record_id: UUID
    ) -> list[FinancialRecordPayment]:
        sql = """
              SELECT *
              FROM financial_record_payments
              WHERE organization_id = %s
                AND financial_record_id = %s
              ORDER BY paid_date ASC, created_at ASC
              """

        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql, (str(organization_id), str(financial_record_id)))
                rows = cur.fetchall()
            return [self._map_row(r) for r in rows]
        finally:
            self._maybe_close(conn)

    def delete(self, *, organization_id: UUID, payment_id: UUID) -> None:
        sql = """
              DELETE FROM financial_record_payments
              WHERE id = %s
                AND organization_id = %s
              """

        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (str(payment_id), str(organization_id)))
            self._maybe_commit(conn)
        except Exception:
            self._maybe_rollback(conn)
            raise
        finally:
            self._maybe_close(conn)

    def delete_all_by_financial_record(
        self, *, organization_id: UUID, financial_record_id: UUID
    ) -> int:
        sql = """
              DELETE FROM financial_record_payments
              WHERE organization_id = %s
                AND financial_record_id = %s
              """

        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (str(organization_id), str(financial_record_id)))
                affected = cur.rowcount
            self._maybe_commit(conn)
            return affected
        except Exception:
            self._maybe_rollback(conn)
            raise
        finally:
            self._maybe_close(conn)

    @staticmethod
    def _map_row(row: dict) -> FinancialRecordPayment:
        return FinancialRecordPayment(
            id=UUID(row["id"]),
            organization_id=UUID(row["organization_id"]),
            financial_record_id=UUID(row["financial_record_id"]),
            amount=Decimal(row["amount"]),
            paid_date=row["paid_date"],
            created_at=row["created_at"],
            created_by_user_id=UUID(row["created_by_user_id"]) if row["created_by_user_id"] else None,
            updated_at=row["updated_at"],
            updated_by_user_id=UUID(row["updated_by_user_id"]) if row["updated_by_user_id"] else None,
        )
