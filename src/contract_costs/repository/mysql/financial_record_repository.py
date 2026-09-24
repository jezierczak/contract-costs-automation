import json
import logging
from decimal import Decimal
from uuid import UUID

from contract_costs.infrastructure.db.mysql_connection import get_connection
from contract_costs.model.document import Document
from contract_costs.model.financial_record import (
    FinancialRecord,
    FinancialRecordStatus,
    PaymentMethod,
    PaymentStatus,
)
from contract_costs.repository.financial_record_repository import FinancialRecordRepository
from contract_costs.repository.mysql.document_mapper import map_row_to_document
from contract_costs.services.financial_records.review.dto.financial_record_review_query import (
    CompanyReviewQuery,
    FinancialRecordReviewQuery,
)

logger = logging.getLogger(__name__)


class MySQLFinancialRecordRepository(FinancialRecordRepository):
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

    def add(self, record: FinancialRecord) -> None:
        sql = """
              INSERT INTO financial_records (
                    id, organization_id, reference, invoice_date, selling_date,
                    buyer_id, seller_id, payment_method, due_date, paid_date,
                    payment_status, status, timestamp, tags, created_at,
                    created_by_user_id, updated_at, updated_by_user_id)
              VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
              """

        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    sql,
                    (
                        str(record.id),
                        str(record.organization_id),
                        record.reference,
                        record.invoice_date,
                        record.selling_date,
                        str(record.buyer_id) if record.buyer_id else None,
                        str(record.seller_id) if record.seller_id else None,
                        record.payment_method.value if record.payment_method else None,
                        record.due_date,
                        record.paid_date,
                        record.payment_status.value if record.payment_status else None,
                        record.status.value,
                        record.timestamp,
                        json.dumps(sorted(record.tags)) if record.tags else None,
                        record.created_at,
                        str(record.created_by_user_id) if record.created_by_user_id else None,
                        record.updated_at,
                        str(record.updated_by_user_id) if record.updated_by_user_id else None,
                    ),
                )
            self._maybe_commit(conn)
        except Exception:
            self._maybe_rollback(conn)
            raise
        finally:
            self._maybe_close(conn)

    def has_documents(self, *, organization_id: UUID, record_id: UUID) -> bool:
        sql = """
              SELECT 1
              FROM documents
              WHERE organization_id = %s
                AND financial_record_id = %s
              LIMIT 1
              """

        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (str(organization_id), str(record_id)))
                return cur.fetchone() is not None
        finally:
            self._maybe_close(conn)

    def get(self, *, organization_id: UUID, record_id: UUID) -> FinancialRecord | None:
        sql = """
              SELECT *
              FROM financial_records
              WHERE id = %s
                AND organization_id = %s
              """

        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql, (str(record_id), str(organization_id)))
                row = cur.fetchone()
        finally:
            self._maybe_close(conn)

        record = self._map_row(row) if row else None
        if not record:
            return None

        self._attach_documents(organization_id=organization_id, records=[record])
        return record

    def exists(self, *, organization_id: UUID, record_id: UUID) -> bool:
        sql = """
              SELECT 1
              FROM financial_records
              WHERE id = %s
                AND organization_id = %s
              LIMIT 1
              """

        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (str(record_id), str(organization_id)))
                return cur.fetchone() is not None
        finally:
            self._maybe_close(conn)

    def get_by_reference(self, *, organization_id: UUID, reference: str) -> list[FinancialRecord]:
        sql = """
              SELECT *
              FROM financial_records
              WHERE organization_id = %s
                AND reference = %s
                AND status != %s
              """

        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql, (str(organization_id), reference, FinancialRecordStatus.DELETED.value))
                rows = cur.fetchall()
        finally:
            self._maybe_close(conn)

        records = [self._map_row(r) for r in rows]
        self._attach_documents(organization_id=organization_id, records=records)
        return records

    def get_unique_record(self, *, organization_id: UUID, reference: str, seller_id: UUID) -> FinancialRecord | None:
        sql = """
        SELECT *
        FROM financial_records
        WHERE organization_id = %s
          AND reference = %s
          AND seller_id = %s
          AND status != %s
        LIMIT 1
        """

        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(
                    sql,
                    (
                        str(organization_id),
                        reference,
                        str(seller_id),
                        FinancialRecordStatus.DELETED.value,
                    ),
                )
                row = cur.fetchone()
        finally:
            self._maybe_close(conn)

        record = self._map_row(row) if row else None
        if not record:
            return None

        self._attach_documents(organization_id=organization_id, records=[record])
        return record

    def list_all(self, *, organization_id: UUID) -> list[FinancialRecord]:
        sql = """
              SELECT *
              FROM financial_records
              WHERE organization_id = %s
              ORDER BY invoice_date DESC, timestamp DESC
              """

        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql, (str(organization_id),))
                rows = cur.fetchall()
        finally:
            self._maybe_close(conn)

        records = [self._map_row(r) for r in rows]
        self._attach_documents(organization_id=organization_id, records=records)
        return records

    def list_by_seller_id(self, *, organization_id: UUID, seller_id: UUID) -> list[FinancialRecord]:
        sql = """
              SELECT *
              FROM financial_records
              WHERE organization_id = %s
                AND seller_id = %s
              """

        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql, (str(organization_id), str(seller_id)))
                rows = cur.fetchall()
        finally:
            self._maybe_close(conn)

        records = [self._map_row(r) for r in rows]
        self._attach_documents(organization_id=organization_id, records=records)
        return records

    def get_for_assignment(
        self,
        *,
        organization_id: UUID,
        status: FinancialRecordStatus | list[FinancialRecordStatus],
    ) -> list[FinancialRecord]:
        statuses = [status] if isinstance(status, FinancialRecordStatus) else list(status)
        if not statuses:
            return []

        placeholders = ", ".join(["%s"] * len(statuses))
        sql = f"""
          SELECT *
          FROM financial_records
          WHERE organization_id = %s
            AND status IN ({placeholders})
          ORDER BY invoice_date
          """
        params = [str(organization_id)] + [s.value for s in statuses]

        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql, params)
                rows = cur.fetchall()
        finally:
            self._maybe_close(conn)

        records = [self._map_row(r) for r in rows]
        self._attach_documents(organization_id=organization_id, records=records)
        return records

    def update(self, record: FinancialRecord) -> None:
        sql = """
              UPDATE financial_records
              SET reference          = %s,
                  invoice_date       = %s,
                  selling_date       = %s,
                  buyer_id           = %s,
                  seller_id          = %s,
                  payment_method     = %s,
                  due_date           = %s,
                  paid_date          = %s,
                  payment_status     = %s,
                  status             = %s,
                  tags               = %s,
                  timestamp          = %s,
                  updated_at         = %s,
                  updated_by_user_id = %s
              WHERE id = %s
                AND organization_id = %s
              """

        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    sql,
                    (
                        record.reference,
                        record.invoice_date,
                        record.selling_date,
                        str(record.buyer_id) if record.buyer_id else None,
                        str(record.seller_id) if record.seller_id else None,
                        record.payment_method.value if record.payment_method else None,
                        record.due_date,
                        record.paid_date,
                        record.payment_status.value if record.payment_status else None,
                        record.status.value,
                        json.dumps(sorted(record.tags)) if record.tags else None,
                        record.timestamp,
                        record.updated_at,
                        str(record.updated_by_user_id) if record.updated_by_user_id else None,
                        str(record.id),
                        str(record.organization_id),
                    ),
                )
            self._maybe_commit(conn)
        except Exception:
            self._maybe_rollback(conn)
            raise
        finally:
            self._maybe_close(conn)

    # def list_for_review(self, *, organization_id: UUID, query: FinancialRecordReviewQuery) -> list[FinancialRecord]:
    #     conditions = ["financial_records.organization_id = %s"]
    #     params: list[object] = [str(organization_id)]
    #
    #     needs_contract_join = bool(query.contract_codes)
    #
    #     if query.buyer_query:
    #         self._apply_company_query(alias="buyer", query=query.buyer_query, conditions=conditions, params=params)
    #
    #     if query.seller_query:
    #         self._apply_company_query(alias="seller", query=query.seller_query, conditions=conditions, params=params)
    #
    #     if query.only_ready_for_accountant:
    #         conditions.append("financial_records.status = %s")
    #         # params.append(FinancialRecordStatus.PROCESSED.value)
    #     elif query.statuses:
    #         placeholders = ", ".join(["%s"] * len(query.statuses))
    #         conditions.append(f"financial_records.status IN ({placeholders})")
    #         params.extend(s.value for s in query.statuses)
    #     else:
    #         conditions.append("financial_records.status != %s")
    #         params.append(FinancialRecordStatus.DELETED.value)
    #
    #     if query.contract_codes:
    #         placeholders = ", ".join(["%s"] * len(query.contract_codes))
    #         conditions.append(f"contracts.code IN ({placeholders})")
    #         params.extend(query.contract_codes)
    #
    #     if query.payment_statuses:
    #         placeholders = ", ".join(["%s"] * len(query.payment_statuses))
    #         conditions.append(f"financial_records.payment_status IN ({placeholders})")
    #         params.extend(p.value for p in query.payment_statuses)
    #
    #     if query.from_date:
    #         conditions.append("financial_records.invoice_date >= %s")
    #         params.append(query.from_date)
    #
    #     if query.to_date:
    #         conditions.append("financial_records.invoice_date <= %s")
    #         params.append(query.to_date)
    #
    #     if query.direction:
    #         conditions.append(
    #             """
    #             CASE
    #                 WHEN buyer.role = 'Own' AND seller.role != 'Own' THEN 'COST'
    #                 WHEN buyer.role != 'Own' AND seller.role = 'Own' THEN 'REVENUE'
    #                 WHEN buyer.role = 'Own' AND seller.role = 'Own' THEN 'INTERNAL'
    #             END = %s
    #             """
    #         )
    #         params.append(query.direction.value)
    #
    #     sql = """
    #           SELECT DISTINCT financial_records.*
    #           FROM financial_records
    #           """
    #
    #     if query.seller_query or query.buyer_query or query.direction:
    #         sql += """
    #             JOIN companies buyer ON buyer.id = financial_records.buyer_id
    #             JOIN companies seller ON seller.id = financial_records.seller_id
    #         """
    #
    #     if needs_contract_join:
    #         sql += """
    #             JOIN financial_record_lines il ON il.financial_record_id = financial_records.id
    #             JOIN contracts ON contracts.id = il.contract_id
    #         """
    #
    #     if conditions:
    #         sql += " WHERE " + " AND ".join(conditions)
    #
    #     if not query.payment_statuses:
    #         sql += " ORDER BY financial_records.invoice_date DESC, financial_records.timestamp DESC"
    #     else:
    #         sql += " ORDER BY financial_records.due_date, financial_records.timestamp"
    #
    #     if query.limit:
    #         sql += " LIMIT %s"
    #         params.append(query.limit)
    #
    #     conn = self._get_connection()
    #     try:
    #         with conn.cursor(dictionary=True) as cur:
    #             logger.info(sql)
    #             logger.info(params)
    #             cur.execute(sql, params)
    #             rows = cur.fetchall()
    #     finally:
    #         self._maybe_close(conn)
    #
    #     records = [self._map_row(r) for r in rows]
    #     self._attach_documents(organization_id=organization_id, records=records)
    #     return records

    def find_by_total(
            self,
            *,
            organization_id: UUID,
            total: Decimal,
            tolerance: Decimal,
            seller_id: UUID | None = None,
    ) -> list[UUID]:

        sql = """
              SELECT frl.financial_record_id
              FROM financial_record_lines frl
                       JOIN financial_records fr ON fr.id = frl.financial_record_id
              WHERE frl.organization_id = %s
                AND frl.financial_record_id IS NOT NULL
                AND fr.status != %s \
              """

        params: list[object] = [
            str(organization_id),
            FinancialRecordStatus.DELETED.value,
        ]

        if seller_id:
            sql += " AND fr.seller_id = %s"
            params.append(str(seller_id))

        sql += """
            GROUP BY frl.financial_record_id
            HAVING ABS(SUM(
                ROUND(
                    CASE
                        WHEN frl.amount_input_type = 'gross' THEN frl.amount_value
                        ELSE (frl.amount_value + (frl.amount_value * frl.vat_rate))
                    END
                , 2)
            ) - %s) <= %s
        """

        params.extend([total, tolerance])

        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                rows = cur.fetchall()
            return [UUID(r[0]) for r in rows]
        finally:
            self._maybe_close(conn)

    def list_for_review(
            self,
            *,
            organization_id: UUID,
            query: FinancialRecordReviewQuery,
    ) -> list[FinancialRecord]:

        sql, params, has_payment_filter = self._build_review_sql(
            organization_id=organization_id,
            query=query,
            select_clause="DISTINCT financial_records.*",
        )

        if not has_payment_filter:
            sql += " ORDER BY financial_records.invoice_date DESC, financial_records.timestamp DESC"
        else:
            sql += " ORDER BY financial_records.due_date, financial_records.timestamp"

        if query.limit:
            sql += " LIMIT %s"
            params.append(query.limit)

        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                logger.debug(sql)
                logger.debug(params)
                cur.execute(sql, params)
                rows = cur.fetchall()
        finally:
            self._maybe_close(conn)

        records = [self._map_row(r) for r in rows]
        self._attach_documents(organization_id=organization_id, records=records)
        return records

    def count_for_review(
            self,
            *,
            organization_id: UUID,
            query: FinancialRecordReviewQuery,
    ) -> int:

        sql, params, _ = self._build_review_sql(
            organization_id=organization_id,
            query=query,
            select_clause="COUNT(DISTINCT financial_records.id) AS cnt",
        )

        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql, params)
                row = cur.fetchone()
                return row["cnt"] if row else 0
        finally:
            self._maybe_close(conn)

    def _build_review_sql(
            self,
            *,
            organization_id: UUID,
            query: FinancialRecordReviewQuery,
            select_clause: str,
    ) -> tuple[str, list[object], bool]:

        conditions = ["financial_records.organization_id = %s"]
        params: list[object] = [str(organization_id)]

        needs_contract_join = bool(query.contract_codes)

        if query.buyer_query and query.seller_query and query.buyer_query == query.seller_query:

            values = query.buyer_query.get("id")

            if values:
                values = values if isinstance(values, list) else [values]
                placeholders = ", ".join(["%s"] * len(values))

                conditions.append(
                    f"(financial_records.buyer_id IN ({placeholders}) "
                    f"OR financial_records.seller_id IN ({placeholders}))"
                )

                params.extend(values)
                params.extend(values)

        else:

            if query.buyer_query:
                self._apply_company_query(
                    alias="buyer",
                    query=query.buyer_query,
                    conditions=conditions,
                    params=params,
                )

            if query.seller_query:
                self._apply_company_query(
                    alias="seller",
                    query=query.seller_query,
                    conditions=conditions,
                    params=params,
                )

        if query.only_ready_for_accountant:
            conditions.append("financial_records.status = %s")
            params.append(FinancialRecordStatus.PROCESSED.value)

        elif query.statuses:
            placeholders = ", ".join(["%s"] * len(query.statuses))
            conditions.append(f"financial_records.status IN ({placeholders})")
            params.extend(s.value for s in query.statuses)

        else:
            conditions.append("financial_records.status != %s")
            params.append(FinancialRecordStatus.DELETED.value)

        if query.contract_codes:
            placeholders = ", ".join(["%s"] * len(query.contract_codes))
            conditions.append(f"contracts.code IN ({placeholders})")
            params.extend(query.contract_codes)

        if query.payment_statuses:
            placeholders = ", ".join(["%s"] * len(query.payment_statuses))
            conditions.append(f"financial_records.payment_status IN ({placeholders})")
            params.extend(p.value for p in query.payment_statuses)

        if query.from_date:
            conditions.append("financial_records.invoice_date >= %s")
            params.append(query.from_date)

        if query.to_date:
            conditions.append("financial_records.invoice_date <= %s")
            params.append(query.to_date)

        if query.direction:
            directions = (
                query.direction
                if isinstance(query.direction, list)
                else [query.direction]
            )

            placeholders = ", ".join(["%s"] * len(directions))

            conditions.append(
                f"""
                (
                    CASE
                        WHEN vt.direction IS NOT NULL THEN vt.direction
                        WHEN buyer.role = 'Own' AND seller.role != 'Own' THEN 'COST'
                        WHEN buyer.role != 'Own' AND seller.role = 'Own' THEN 'REVENUE'
                        WHEN buyer.role = 'Own' AND seller.role = 'Own' THEN 'INTERNAL'
                        ELSE NULL
                    END
                ) IN ({placeholders})
                """
            )
            params.extend([d.value for d in directions])

        sql = f"""
            SELECT {select_clause}
            FROM financial_records
        """

        sql += """
            LEFT JOIN financial_record_lines l ON l.financial_record_id = financial_records.id
            LEFT JOIN value_types vt ON vt.id = l.value_type_id
        """

        if query.seller_query or query.buyer_query or query.direction:
            sql += """
                JOIN companies buyer ON buyer.id = financial_records.buyer_id
                JOIN companies seller ON seller.id = financial_records.seller_id
            """

        if needs_contract_join:
            sql += """
                JOIN contracts ON contracts.id = l.contract_id
            """

        if conditions:
            sql += " WHERE " + " AND ".join(conditions)

        return sql, params, bool(query.payment_statuses)

    @staticmethod
    def _map_row(row: dict) -> FinancialRecord:
        return FinancialRecord(
            id=UUID(row["id"]),
            organization_id=UUID(row["organization_id"]),
            reference=row["reference"],
            invoice_date=row["invoice_date"],
            selling_date=row["selling_date"],
            buyer_id=UUID(row["buyer_id"]),
            seller_id=UUID(row["seller_id"]),
            payment_method=PaymentMethod(row["payment_method"]),
            due_date=row["due_date"],
            paid_date=row["paid_date"],
            payment_status=PaymentStatus(row["payment_status"]),
            status=FinancialRecordStatus(row["status"]),
            timestamp=row["timestamp"],
            tags=set(json.loads(row["tags"])) if row["tags"] else set(),
            created_at=row["created_at"],
            created_by_user_id=UUID(row["created_by_user_id"]) if row["created_by_user_id"] else None,
            updated_at=row["updated_at"],
            updated_by_user_id=UUID(row["updated_by_user_id"]) if row["updated_by_user_id"] else None,
            documents=[],
        )

    @staticmethod
    def _apply_company_query(
        *,
        alias: str,
        query: CompanyReviewQuery,
        conditions: list[str],
        params: list[object],
    ) -> None:
        column_map = {
            "name": f"{alias}.name",
            "tax_numbers": f"{alias}.tax_number",
            "role": f"{alias}.role",
        }

        any_search_columns = ("name", "tax_number", "description", "email", "street", "city")

        for key, value in query.items():
            if key == "any":
                or_conditions = [f"{alias}.{col} LIKE %s" for col in any_search_columns]
                conditions.append("(" + " OR ".join(or_conditions) + ")")
                like = f"%{value}%"
                params.extend([like] * len(or_conditions))
                continue

            values = value if isinstance(value, list) else [value]
            column = column_map.get(key)
            if not column:
                continue

            if key == "name":
                or_conditions = [f"{column} LIKE %s" for _ in values]
                conditions.append("(" + " OR ".join(or_conditions) + ")")
                for v in values:
                    params.append(f"%{v.value}%" if hasattr(v, "value") else f"%{v}%")
                continue

            placeholders = ", ".join(["%s"] * len(values))
            conditions.append(f"{column} IN ({placeholders})")
            for v in values:
                params.append(v.value if hasattr(v, "value") else v)

    def _attach_documents(self, *, organization_id: UUID, records: list[FinancialRecord]) -> None:
        if not records:
            return

        record_ids = [r.id for r in records]
        docs = self._load_documents(organization_id, record_ids)

        for r in records:
            r.documents = docs.get(r.id, [])

    def _load_documents(self, organization_id: UUID, record_ids: list[UUID]) -> dict[UUID, list[Document]]:
        if not record_ids:
            return {}

        placeholders = ",".join(["%s"] * len(record_ids))
        sql = f"""
            SELECT *
            FROM documents
            WHERE organization_id = %s
              AND financial_record_id IN ({placeholders})
        """

        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql, (str(organization_id), *[str(i) for i in record_ids]))
                rows = cur.fetchall()
        finally:
            self._maybe_close(conn)

        result: dict[UUID, list[Document]] = {}
        for r in rows:
            doc = self._map_row_to_document(r)
            if doc.financial_record_id:
                result.setdefault(doc.financial_record_id, []).append(doc)
        return result

    @staticmethod
    def _map_row_to_document(row: dict) -> Document:
        return map_row_to_document(row)
