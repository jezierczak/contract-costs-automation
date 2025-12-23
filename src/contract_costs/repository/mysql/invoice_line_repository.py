from decimal import Decimal
from uuid import UUID

from contract_costs.model.invoice import InvoiceStatus
from contract_costs.model.invoice_line import InvoiceLine
from contract_costs.model.amount import Amount, VatRate, TaxTreatment
from contract_costs.model.unit_of_measure import UnitOfMeasure
from contract_costs.repository.invoice_line_repository import InvoiceLineRepository
from contract_costs.infrastructure.db.mysql_connection import get_connection


class MySQLInvoiceLineRepository(InvoiceLineRepository):

    def add(self, invoice_line: InvoiceLine) -> None:
        sql = """
        INSERT INTO invoice_lines (
            id,
            invoice_id,
            contract_id,
            cost_node_id,
            cost_type_id,
            item_name,
            quantity,
            unit,
            amount_value,
            vat_rate,
            tax_treatment,
            description
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(
                sql,
                (
                    str(invoice_line.id),
                    str(invoice_line.invoice_id) if invoice_line.invoice_id else None,
                    str(invoice_line.contract_id) if invoice_line.contract_id else None,
                    str(invoice_line.cost_node_id) if invoice_line.cost_node_id else None,
                    str(invoice_line.cost_type_id) if invoice_line.cost_type_id else None,
                    invoice_line.item_name,
                    invoice_line.quantity,
                    invoice_line.unit.value if invoice_line.unit else None,
                    invoice_line.amount.value,
                    invoice_line.amount.vat_rate.value if invoice_line.amount.vat_rate else None,
                    invoice_line.amount.tax_treatment.value,
                    invoice_line.description,
                ),
            )
        conn.commit()

    def get(self, invoice_line_id: UUID) -> InvoiceLine | None:
        sql = "SELECT * FROM invoice_lines WHERE id = %s"

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (str(invoice_line_id),))
            row = cur.fetchone()

        return self._map_row(row) if row else None



    def list_lines(self) -> list[InvoiceLine]:
        sql = "SELECT * FROM invoice_lines"

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql)
            rows = cur.fetchall()

        return [self._map_row(r) for r in rows]

    def list_by_contract(self, contract_id: UUID) -> list[InvoiceLine]:
        sql = "SELECT * FROM invoice_lines WHERE contract_id = %s"

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (str(contract_id),))
            rows = cur.fetchall()

        return [self._map_row(r) for r in rows]

    def list_by_invoice(self, invoice_id: UUID) -> list[InvoiceLine]:
        sql = "SELECT * FROM invoice_lines WHERE invoice_id = %s"

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (str(invoice_id),))
            rows = cur.fetchall()

        return [self._map_row(r) for r in rows]

    def list_by_invoice_ids(self, invoice_line_ids: list[UUID]) -> list[InvoiceLine] | None:
        result: list[InvoiceLine] = []

        for invoice_id in invoice_line_ids:
            result.extend(self.list_by_invoice(invoice_id))

        return result

    def list_by_null_invoice(self) -> list[InvoiceLine] | None:
        sql = "SELECT * FROM invoice_lines WHERE invoice_id is NULL"

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql,())
            rows = cur.fetchall()

        return [self._map_row(r) for r in rows]

    def update(self, invoice_line: InvoiceLine) -> None:
        sql = """
        UPDATE invoice_lines SET
            invoice_id = %s,
            contract_id = %s,
            cost_node_id = %s,
            cost_type_id = %s,
            item_name = %s,
            quantity = %s,
            unit = %s,
            amount_value = %s,
            vat_rate = %s,
            tax_treatment = %s,
            description = %s
        WHERE id = %s
        """

        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(
                sql,
                (
                    str(invoice_line.invoice_id) if invoice_line.invoice_id else None,
                    str(invoice_line.contract_id) if invoice_line.contract_id else None,
                    str(invoice_line.cost_node_id) if invoice_line.cost_node_id else None,
                    str(invoice_line.cost_type_id) if invoice_line.cost_type_id else None,
                    invoice_line.item_name,
                    invoice_line.quantity,
                    invoice_line.unit.value if invoice_line.unit else None,
                    invoice_line.amount.value,
                    invoice_line.amount.vat_rate.value if invoice_line.amount.vat_rate else None,
                    invoice_line.amount.tax_treatment.value,
                    invoice_line.description,
                    str(invoice_line.id),
                ),
            )
        conn.commit()

    def exists(self, invoice_line_id: UUID) -> bool:
        sql = "SELECT 1 FROM invoice_lines WHERE id = %s LIMIT 1"

        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(sql, (str(invoice_line_id),))
            return cur.fetchone() is not None

    def get_for_assignment(self) -> list[InvoiceLine]:
        sql = """
        SELECT *
        FROM invoice_lines
        WHERE cost_node_id IS NULL
           OR cost_type_id IS NULL
        """

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql)
            rows = cur.fetchall()

        return [self._map_row(r) for r in rows]

    # ---------- mapping ----------
    @staticmethod
    def _map_row( row: dict) -> InvoiceLine:
        return InvoiceLine(
            id=UUID(row["id"]),
            invoice_id=UUID(row["invoice_id"]) if row["invoice_id"] else None,
            contract_id=UUID(row["contract_id"]) if row["contract_id"] else None,
            cost_node_id=UUID(row["cost_node_id"]) if row["cost_node_id"] else None,
            cost_type_id=UUID(row["cost_type_id"]) if row["cost_type_id"] else None,
            item_name=row["item_name"],
            quantity=row["quantity"],
            unit=UnitOfMeasure(row["unit"]) if row["unit"] else None,  # value
            amount=Amount(
                value=row["amount_value"],
                vat_rate=VatRate(Decimal(row["vat_rate"])) if row["vat_rate"] is not None else VatRate.VAT_ZW,
                tax_treatment=TaxTreatment(row["tax_treatment"]),
            ),
            description=row["description"],
        )
