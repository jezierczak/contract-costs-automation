from uuid import UUID
from datetime import datetime

from contract_costs.model.invoice import (
    Invoice,
    InvoiceStatus,
    PaymentMethod,
    PaymentStatus,
)
from contract_costs.repository.invoice_repository import InvoiceRepository
from contract_costs.infrastructure.db.mysql_connection import get_connection


class MySQLInvoiceRepository(InvoiceRepository):

    def add(self, invoice: Invoice) -> None:
        sql = """
        INSERT INTO invoices (
            id,
            invoice_number,
            invoice_date,
            selling_date,
            buyer_id,
            seller_id,
            payment_method,
            due_date,
            payment_status,
            status,
            timestamp
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(
                sql,
                (
                    str(invoice.id),
                    invoice.invoice_number,
                    invoice.invoice_date,
                    invoice.selling_date,
                    str(invoice.buyer_id),
                    str(invoice.seller_id),
                    invoice.payment_method.value,
                    invoice.due_date,
                    invoice.payment_status.value,
                    invoice.status.value,
                    invoice.timestamp,
                ),
            )
        conn.commit()

    def get(self, invoice_id: UUID) -> Invoice | None:
        sql = "SELECT * FROM invoices WHERE id = %s"

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (str(invoice_id),))
            row = cur.fetchone()

        return self._map_row(row) if row else None

    def get_by_invoice_number(self, invoice_number: str) -> Invoice | None:
        sql = "SELECT * FROM invoices WHERE invoice_number = %s"

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (str(invoice_number),))
            row = cur.fetchone()

        return self._map_row(row) if row else None

    def get_unique_invoice(self, invoice_number: str,seller_id: UUID) -> Invoice | None:
        sql = "SELECT * FROM invoices WHERE invoice_number = %s AND seller_id = %s"

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (str(invoice_number),str(seller_id)))
            row = cur.fetchone()

        return self._map_row(row) if row else None

    def list_invoices(self) -> list[Invoice]:
        sql = "SELECT * FROM invoices ORDER BY invoice_date DESC"

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql)
            rows = cur.fetchall()

        return [self._map_row(r) for r in rows]

    def update(self, invoice: Invoice) -> None:
        sql = """
        UPDATE invoices SET
            invoice_number = %s,
            invoice_date = %s,
            selling_date = %s,
            buyer_id = %s,
            seller_id = %s,
            payment_method = %s,
            due_date = %s,
            payment_status = %s,
            status = %s,
            timestamp = %s
        WHERE id = %s
        """

        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(
                sql,
                (
                    invoice.invoice_number,
                    invoice.invoice_date,
                    invoice.selling_date,
                    str(invoice.buyer_id),
                    str(invoice.seller_id),
                    invoice.payment_method.value,
                    invoice.due_date,
                    invoice.payment_status.value,
                    invoice.status.value,
                    invoice.timestamp,
                    str(invoice.id),
                ),
            )
        conn.commit()

    def exists(self, invoice_id: UUID) -> bool:
        sql = "SELECT 1 FROM invoices WHERE id = %s LIMIT 1"

        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(sql, (str(invoice_id),))
            return cur.fetchone() is not None

    def get_for_assignment(self, status: InvoiceStatus | list[InvoiceStatus]) -> list[Invoice]:
        # --- normalizacja wejścia ---
        if isinstance(status, InvoiceStatus):
            statuses = [status]
        else:
            statuses = list(status)

        if not statuses:
            return []

        status_values = [s.value for s in statuses]
        # --- dynamiczne placeholders (%s, %s, ...) ---
        placeholders = ", ".join(["%s"] * len(status_values))

        sql = f"""
        SELECT *
        FROM invoices
        WHERE status IN ({placeholders})
        ORDER BY invoice_date
        """

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, status_values)
            rows = cur.fetchall()

        return [self._map_row(r) for r in rows]

    # ---------- mapping ----------
    @staticmethod
    def _map_row( row: dict) -> Invoice:
        return Invoice(
            id=UUID(row["id"]),
            invoice_number=row["invoice_number"],
            invoice_date=row["invoice_date"],
            selling_date=row["selling_date"],
            buyer_id=UUID(row["buyer_id"]),
            seller_id=UUID(row["seller_id"]),
            payment_method=PaymentMethod(row["payment_method"]),
            due_date=row["due_date"],
            payment_status=PaymentStatus(row["payment_status"]),
            status=InvoiceStatus(row["status"]),
            timestamp=row["timestamp"],
        )
