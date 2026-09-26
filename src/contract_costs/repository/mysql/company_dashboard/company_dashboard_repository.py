import logging
from datetime import date
from uuid import UUID

from contract_costs.infrastructure.db.mysql_connection import get_connection
from contract_costs.repository.company_dashboard.company_dashboard_repository import (
    CompanyDashboardRepository,
)
from contract_costs.repository.company_dashboard.dto.company_ledger_line_raw import CompanyLedgerLineRaw
from contract_costs.repository.company_dashboard.dto.counterparty_ledger_line_raw import CounterpartyLedgerLineRaw

logger = logging.getLogger(__name__)


class MySQLCompanyDashboardRepository(CompanyDashboardRepository):

    def __init__(self, connection=None) -> None:
        self._connection = connection

    def _get_connection(self):
        return self._connection or get_connection()

    def _maybe_close(self, conn) -> None:
        if self._connection is None:
            conn.close()

    def fetch_company_lines(
            self,
            *,
            organization_id: UUID,
            company_id: UUID,
            start: date,
            end: date,
    ) -> list[CompanyLedgerLineRaw]:

        sql = """
              SELECT fl.record_id,
                     fl.record_date,
                     fl.buyer_id,
                     fl.seller_id,
                     fl.direction,
                     fl.contract_type,
                     fl.contract_owner_id,
                     fl.value_type_id,
                     fl.value_type_code,
                     fl.value_type_name,
                     fl.item_name,
                     fl.description,
                     fl.amount_value,
                     fl.amount_input_type,
                     fl.vat_rate,
                     fl.tax_treatment,
                     fl.status

              FROM financial_ledger fl

              WHERE fl.organization_id = %(org)s
                AND fl.record_date >= %(start)s
                AND fl.record_date < %(end)s
                AND (
                    fl.buyer_id = %(company)s
                    OR fl.seller_id = %(company)s
                    OR (fl.contract_type = 'system'    -- LEGACY: koszty stałe na kontrakcie systemowym
                        AND fl.contract_owner_id = %(company)s)
                )
              """

        conn = self._get_connection()

        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql, {
                    "org": str(organization_id),
                    "company": str(company_id),
                    "start": start,
                    "end": end,
                })
                rows = cur.fetchall()

        finally:
            self._maybe_close(conn)

        return [
            CompanyLedgerLineRaw(
                record_id=r["record_id"],
                record_date=r["record_date"],
                buyer_id=r["buyer_id"],
                seller_id=r["seller_id"],
                direction=r["direction"],
                contract_type=r["contract_type"],
                contract_owner_id=r["contract_owner_id"],
                value_type_id=r["value_type_id"],
                value_type_code=r["value_type_code"],
                value_type_name=r["value_type_name"],
                item_name=r["item_name"],
                description=r["description"],
                amount_value=r["amount_value"],
                amount_input_type=r["amount_input_type"],
                vat_rate=r["vat_rate"],
                tax_treatment=r["tax_treatment"],
                status=r["status"],
            )
            for r in rows
        ]

    def fetch_counterparty_lines(
            self,
            *,
            organization_id: UUID,
            counterparty_id: UUID,
            owner_company_id: UUID | None,
    ) -> list[CounterpartyLedgerLineRaw]:

        sql = """
              SELECT fl.record_id, 
                     fl.record_date, 
                     fl.buyer_id, 
                     fl.seller_id, 
                     fl.amount_value, 
                     fl.amount_input_type, 
                     fl.vat_rate, 
                     fl.tax_treatment, 
                     fl.payment_status

              FROM financial_ledger fl

              WHERE fl.organization_id = %(org)s
                AND (
                  fl.buyer_id = %(counterparty)s
                      OR fl.seller_id = %(counterparty)s
                  )
                  AND (
                        %(owner_company)s IS NULL
                        OR (
                            fl.buyer_id = %(counterparty)s
                            AND fl.seller_id = %(owner_company)s
                        )
                        OR (
                            fl.seller_id = %(counterparty)s
                            AND fl.buyer_id = %(owner_company)s
                        )
                    )
                AND fl.status != 'deleted' 
              """

        conn = self._get_connection()

        try:
            with conn.cursor(dictionary=True) as cur:

                params = {
                    "org": str(organization_id),
                    "counterparty": str(counterparty_id),
                    "owner_company": str(owner_company_id) if owner_company_id else None
                }

                cur.execute(sql, params)
                rows = cur.fetchall()

        finally:
            self._maybe_close(conn)

        result: list[CounterpartyLedgerLineRaw] = []

        for r in rows:
            result.append(
                CounterpartyLedgerLineRaw(
                    record_id=r["record_id"],
                    record_date=r["record_date"],
                    buyer_id=r["buyer_id"],
                    seller_id=r["seller_id"],
                    amount_value=r["amount_value"],
                    amount_input_type=r["amount_input_type"],
                    vat_rate=r["vat_rate"],
                    tax_treatment=r["tax_treatment"],
                    payment_status=r["payment_status"],

                )
            )

        return result

