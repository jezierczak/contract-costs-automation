from datetime import datetime, date
from decimal import Decimal
from uuid import UUID

from contract_costs.model.financial_record_line import FinancialRecordLine
from contract_costs.model.amount import Amount, VatRate, TaxTreatment
from contract_costs.model.unit_of_measure import UnitOfMeasure
from contract_costs.repository.financial_record_line_repository import FinancialRecordLineRepository
from contract_costs.infrastructure.db.mysql_connection import get_connection


class MySQLFinancialRecordLineRepository(FinancialRecordLineRepository):

    def add(
        self,
        *,
        organization_id: UUID,
        line: FinancialRecordLine,
    ) -> None:
        sql = """
        INSERT INTO financial_record_lines (
            id,
            organization_id,
            financial_record_id,
            contract_id,
            contract_node_id,
            value_type_id,
            item_name,
            quantity,
            unit,
            amount_value,
            vat_rate,
            tax_treatment,
            description,
            created_at,
            created_by_user_id,
            updated_at,
            updated_by_user_id
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(
                sql,
                (
                    str(line.id),
                    str(organization_id),
                    str(line.financial_record_id) if line.financial_record_id else None,
                    str(line.contract_id) if line.contract_id else None,
                    str(line.contract_node_id) if line.contract_node_id else None,
                    str(line.value_type_id) if line.value_type_id else None,
                    line.item_name,
                    line.quantity,
                    line.unit.value if line.unit else None,
                    line.amount.value,
                    line.amount.vat_rate.value,
                    line.amount.tax_treatment.value,
                    line.description,
                    line.created_at,
                    str(line.created_by_user_id) if line.created_by_user_id else None,
                    line.updated_at,
                    str(line.updated_by_user_id) if line.updated_by_user_id else None,
                ),
            )
        conn.commit()

    def get(
            self,
            *,
            organization_id: UUID,
            line_id: UUID,
    ) -> FinancialRecordLine | None:
        sql = """
              SELECT *
              FROM financial_record_lines
              WHERE id = %s
                AND organization_id = %s 
              """

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (str(line_id), str(organization_id)))
            row = cur.fetchone()

        return self._map_row(row) if row else None

    def exists(
            self,
            *,
            organization_id: UUID,
            line_id: UUID,
    ) -> bool:
        sql = """
              SELECT 1
              FROM financial_record_lines
              WHERE id = %s
                AND organization_id = %s
              LIMIT 1 
              """

        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(sql, (str(line_id), str(organization_id)))
            return cur.fetchone() is not None

    def list_all(self,*, organization_id: UUID) -> list[FinancialRecordLine]:
        sql = "SELECT * FROM financial_record_lines where organization_id = %s"

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql,(str(organization_id),))
            rows = cur.fetchall()

        return [self._map_row(r) for r in rows]

    def list_by_contract(self,*, organization_id: UUID, contract_id: UUID) -> list[FinancialRecordLine]:
        sql = "SELECT * FROM financial_record_lines WHERE contract_id = %s AND organization_id = %s"

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (str(contract_id),str(organization_id)))
            rows = cur.fetchall()

        return [self._map_row(r) for r in rows]

    def list_by_financial_record(
            self,
            *,
            organization_id: UUID,
            financial_record_id: UUID,
    ) -> list[FinancialRecordLine]:
        sql = """
              SELECT *
              FROM financial_record_lines
              WHERE organization_id = %s
                AND financial_record_id = %s 
              """

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (str(organization_id), str(financial_record_id)))
            rows = cur.fetchall()

        return [self._map_row(r) for r in rows]

    def list_by_financial_record_ids(
            self,
            *,
            organization_id: UUID,
            financial_records_ids: list[UUID]
    ) -> list[FinancialRecordLine]:

        if not financial_records_ids:
            return []

        placeholders = ", ".join(["%s"] * len(financial_records_ids))
        sql = f"""
            SELECT *
            FROM financial_record_lines
            WHERE organization_id = %s
              AND financial_record_id IN ({placeholders})
        """

        params = [str(organization_id), *map(str, financial_records_ids)]

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()

        return [self._map_row(r) for r in rows]

    def list_by_null_invoice(self,*, organization_id: UUID) -> list[FinancialRecordLine]:
        sql = "SELECT * FROM financial_record_lines WHERE financial_record_id is NULL and organization_id = %s"

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql,(str(organization_id),))
            rows = cur.fetchall()

        return [self._map_row(r) for r in rows]

    def update(
            self,
            *,
            organization_id: UUID,
            line: FinancialRecordLine,
    ) -> None:
        sql = """
              UPDATE financial_record_lines
              SET financial_record_id = %s,
                  contract_id         = %s,
                  contract_node_id    = %s,
                  value_type_id       = %s,
                  item_name           = %s,
                  quantity            = %s,
                  unit                = %s,
                  amount_value        = %s,
                  vat_rate            = %s,
                  tax_treatment       = %s,
                  description         = %s,
                  updated_at          = %s,
                  updated_by_user_id  = %s
              WHERE id = %s
                AND organization_id = %s \
              """

        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(
                sql,
                (
                    str(line.financial_record_id) if line.financial_record_id else None,
                    str(line.contract_id) if line.contract_id else None,
                    str(line.contract_node_id) if line.contract_node_id else None,
                    str(line.value_type_id) if line.value_type_id else None,
                    line.item_name,
                    line.quantity,
                    line.unit.value if line.unit else None,
                    line.amount.value,
                    line.amount.vat_rate.value,
                    line.amount.tax_treatment.value,
                    line.description,
                    line.updated_at,
                    str(line.updated_by_user_id) if line.updated_by_user_id else None,
                    str(line.id),
                    str(organization_id),
                ),
            )
        conn.commit()


    def list_unassigned(
        self,
        *,
        organization_id: UUID,
    ) -> list[FinancialRecordLine]:
        sql = """
        SELECT *
        FROM financial_record_lines
        WHERE organization_id = %s
          AND financial_record_id IS NULL
        """

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (str(organization_id),))
            rows = cur.fetchall()

        return [self._map_row(r) for r in rows]

    def delete_not_in_ids(
            self,
            *,
            organization_id: UUID,
            financial_record_id: UUID,
            keep_ids: set[UUID],
    ) -> int:

        if not keep_ids:
            sql = "DELETE FROM financial_record_lines WHERE financial_record_id = %s and organization_id = %s"
            params = (str(financial_record_id),str(organization_id))
        else:
            placeholders = ", ".join(["%s"] * len(keep_ids))
            sql = f"""
                DELETE FROM financial_record_lines
                WHERE financial_record_id = %s and organization_id = %s
                AND id NOT IN ({placeholders})
            """
            params = (str(financial_record_id),str(organization_id), *map(str, keep_ids)) #type: ignore

        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(sql, params)
            conn.commit()
            return cur.rowcount


    def get_for_assignment(self,*,organization_id: UUID) -> list[FinancialRecordLine]:
        sql = """
        SELECT *
        FROM financial_record_lines
        WHERE organization_id = %s
             AND (
                contract_node_id IS NULL
                OR value_type_id IS NULL
                )
        """

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql,(str(organization_id),))
            rows = cur.fetchall()

        return [self._map_row(r) for r in rows]

    def list_by_contract_until(
            self,
            *,
            organization_id: UUID,
            contract_id: UUID,
            snapshot_date: date,
    ) -> list[FinancialRecordLine]:

        cutoff = datetime.combine(snapshot_date, datetime.max.time())

        sql = """
              SELECT *
              FROM financial_record_lines
              WHERE organization_id = %s
                AND contract_id = %s
                AND created_at <= %s 
              """

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(
                sql,
                (str(organization_id), str(contract_id), cutoff),
            )
            rows = cur.fetchall()

        return [self._map_row(r) for r in rows]

    # ---------- mapping ----------
    @staticmethod
    def _map_row(row: dict) -> FinancialRecordLine:
        return FinancialRecordLine(
            id=UUID(row["id"]),
            organization_id=UUID(row["organization_id"]),
            financial_record_id=UUID(row["financial_record_id"]) if row["financial_record_id"] else None,
            contract_id=UUID(row["contract_id"]) if row["contract_id"] else None,
            contract_node_id=UUID(row["contract_node_id"]) if row["contract_node_id"] else None,
            value_type_id=UUID(row["value_type_id"]) if row["value_type_id"] else None,
            item_name=row["item_name"],
            quantity=row["quantity"],
            unit=UnitOfMeasure(row["unit"]) if row["unit"] else None,
            amount=Amount(
                value=row["amount_value"],
                vat_rate=VatRate(Decimal(row["vat_rate"])),
                tax_treatment=TaxTreatment(row["tax_treatment"]),
            ),
            description=row["description"],
            created_at=row["created_at"],
            created_by_user_id=UUID(row["created_by_user_id"]) if row["created_by_user_id"] else None,
            updated_at=row["updated_at"],
            updated_by_user_id=UUID(row["updated_by_user_id"]) if row["updated_by_user_id"] else None,
        )

