import logging
from uuid import UUID

from contract_costs.model.invoice import (
    Invoice,
    InvoiceStatus,
    PaymentMethod,
    PaymentStatus,
)
from contract_costs.repository.invoice_repository import InvoiceRepository
from contract_costs.infrastructure.db.mysql_connection import get_connection
from contract_costs.services.invoices.review.dto.invoice_review_query import InvoiceReviewQuery, CompanyReviewQuery

logger = logging.getLogger(__name__)

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

    def get_by_invoice_number(self, invoice_number: str) -> list[Invoice]:
        sql = "SELECT * FROM invoices WHERE invoice_number = %s and status != %s"

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (str(invoice_number),InvoiceStatus.DELETED.value))
            rows = cur.fetchall()

        return [self._map_row(row) for row in rows]

    def get_unique_invoice(self, invoice_number: str,seller_id: UUID) -> Invoice | None:
        sql = "SELECT * FROM invoices WHERE invoice_number = %s AND seller_id = %s AND status != %s"

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (str(invoice_number),str(seller_id), InvoiceStatus.DELETED.value))
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

    def list_by_seller_id(self, seller_id: UUID) -> list[Invoice]:
        sql = "SELECT * FROM invoices WHERE seller_id = %s"

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (str(seller_id),))
            rows = cur.fetchall()

        return [self._map_row(r) for r in rows]

    def list_for_review(self, query: InvoiceReviewQuery) -> list[Invoice]:
        conditions: list[str] = []
        params: list[object] = []

        # ---- BUYER ----
        if query.buyer_query:
            self._apply_company_query(
                alias="buyer",
                query=query.buyer_query,
                conditions=conditions,
                params=params,
            )

        # ---- SELLER ----
        if query.seller_query:
            self._apply_company_query(
                alias="seller",
                query=query.seller_query,
                conditions=conditions,
                params=params,
            )

        # ---- STATUS ----
        if query.only_ready_for_accountant:
            conditions.append("status = %s")
            params.append(InvoiceStatus.PROCESSED.value)

        elif query.statuses:
            placeholders = ", ".join(["%s"] * len(query.statuses))
            conditions.append(f"status IN ({placeholders})")
            params.extend(s.value for s in query.statuses)
        else:
            conditions.append("status != %s")
            params.append(InvoiceStatus.DELETED.value)

        # ---- PAYMENT STATUS ----
        if query.payment_statuses:
            placeholders = ", ".join(["%s"] * len(query.payment_statuses))
            conditions.append(f"payment_status IN ({placeholders})")
            params.extend(p.value for p in query.payment_statuses)

        # ---- DATE FROM ----
        if query.from_date:
            conditions.append("invoice_date >= %s")
            params.append(query.from_date)

        # ---- DATE TO ----
        if query.to_date:
            conditions.append("invoice_date <= %s")
            params.append(query.to_date)

        # # ---- ONLY READY FOR ACCOUNTANT ----
        # if query.only_ready_for_accountant:
        #     conditions.append("status = %s")
        #     params.append(InvoiceStatus.PROCESSED.value)

        # ---- BUILD SQL ----

        if query.seller_query or query.buyer_query:
            sql = """
                  SELECT invoices.*
                  FROM invoices
                           JOIN companies buyer ON buyer.id = invoices.buyer_id
                           JOIN companies seller ON seller.id = invoices.seller_id
                  """
        else:
            sql = "SELECT * FROM invoices"

        if conditions:
            sql += " WHERE " + " AND ".join(conditions)

        sql += " ORDER BY invoice_date DESC, timestamp DESC"

        # ---- EXECUTE ----
        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            logger.info(sql)
            logger.info(params)
            cur.execute(sql, params)
            rows = cur.fetchall()

        return [self._map_row(row) for row in rows]

    @staticmethod
    def _apply_company_query(
            *,
            alias: str,  # "buyer" albo "seller"
            query: CompanyReviewQuery,
            conditions: list[str],
            params: list[object],
    ) -> None:
        column_map = {
            "name": f"{alias}.name",
            "tax_numbers": f"{alias}.tax_number",
            "role": f"{alias}.role",
        }
        ANY_SEARCH_COLUMNS = (
            "name",
            "tax_number",
            "description",
            "email",
            "street",
            "city",
        )

        for key, value in query.items():

            # ---- ANY ----
            if key == "any":
                or_conditions = [
                    f"{alias}.{col} LIKE %s"
                    for col in ANY_SEARCH_COLUMNS
                ]
                conditions.append("(" + " OR ".join(or_conditions) + ")")

                like = f"%{value}%"
                params.extend([like] * len(or_conditions))
                continue

            values = value if isinstance(value, list) else [value]
            column = column_map.get(key)
            if not column:
                continue

            # ---- NAME → LIKE ----
            if key == "name":
                or_conditions = [f"{column} LIKE %s" for _ in values]
                conditions.append("(" + " OR ".join(or_conditions) + ")")

                for v in values:
                    params.append(
                        f"%{v.value}%" if hasattr(v, "value") else f"%{v}%"
                    )
                continue

            # ---- REST → IN ----
            placeholders = ", ".join(["%s"] * len(values))
            conditions.append(f"{column} IN ({placeholders})")

            for v in values:
                params.append(v.value if hasattr(v, "value") else v)



