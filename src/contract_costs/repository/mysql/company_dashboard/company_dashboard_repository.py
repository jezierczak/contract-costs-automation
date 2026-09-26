import logging
from datetime import date
from decimal import Decimal
from uuid import UUID

from contract_costs.infrastructure.db.mysql_connection import get_connection
from contract_costs.repository.company_dashboard.dto.company_dashboard_raw_data import (
    CompanyDashboardRawData,
    CompanyDashboardMonthRaw,
)
from contract_costs.repository.company_dashboard.company_dashboard_repository import (
    CompanyDashboardRepository,
)
from contract_costs.repository.company_dashboard.dto.company_fixed_cost_raw import CompanyFixedCostRaw
from contract_costs.repository.company_dashboard.dto.company_ledger_line_raw import CompanyLedgerLineRaw
from contract_costs.repository.company_dashboard.dto.company_month_breakdown_raw import CompanyMonthBreakdownRaw
from contract_costs.repository.company_dashboard.dto.counterparty_ledger_line_raw import CounterpartyLedgerLineRaw
from contract_costs.repository.company_dashboard.dto.counterparty_summary_raw import CounterpartySummaryRaw
from contract_costs.repository.company_dashboard.dto.counterparty_year_raw import CounterpartyYearRaw

logger = logging.getLogger(__name__)

def _period_range(year: int, month: int | None) -> tuple[date, date]:
    if month:
        start = date(year, month, 1)

        if month == 12:
            end = date(year + 1, 1, 1)
        else:
            end = date(year, month + 1, 1)

    else:
        start = date(year, 1, 1)
        end = date(year + 1, 1, 1)

    return start, end

MONTH_NAMES = [
    "",
    "Styczeń",
    "Luty",
    "Marzec",
    "Kwiecień",
    "Maj",
    "Czerwiec",
    "Lipiec",
    "Sierpień",
    "Wrzesień",
    "Październik",
    "Listopad",
    "Grudzień",
]


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
                     fl.tax_treatment

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
            )
            for r in rows
        ]

    def fetch_dashboard_data(
            self,
            *,
            organization_id: UUID,
            company_id: UUID,
            year: int,
    ) -> CompanyDashboardRawData:

        year_start, year_end = _period_range(year, None)

        sql = """
              SELECT MONTH(fl.record_date) AS month, 

                     SUM( 
                             CASE 
                                 WHEN fl.direction = 'REVENUE' 
                                     THEN fl.amount_value 
                                 ELSE 0 
                                 END 
                     )                     AS revenue, 

                     SUM( 
                             CASE 
                                 WHEN fl.direction = 'COST' 
                                     AND fl.tax_treatment = 'tax_deductible' 
                                     THEN fl.amount_value 
                                 ELSE 0 
                                 END 
                     )                     AS costs, 

                     SUM( 
                             CASE 
                                 WHEN fl.direction = 'COST' 
                                     AND fl.tax_treatment = 'non_deductible' 
                                     THEN fl.amount_value 
                                 ELSE 0 
                                 END 
                     )                     AS non_deductible, 
                   SUM(
                        CASE
                            WHEN fl.direction = 'INTERNAL'
                            AND fl.seller_id = %(company)s
                            THEN fl.amount_value
                            ELSE 0
                        END
                    ) AS internal_revenue,
                    
                    SUM(
                        CASE
                            WHEN fl.direction = 'INTERNAL'
                            AND fl.buyer_id = %(company)s
                            THEN fl.amount_value
                            ELSE 0
                        END
                    ) AS internal_cost,
                     SUM( 
                             CASE 
                                 WHEN fl.direction = 'FIXED' 
                                     OR (fl.contract_type = 'system'
                                     AND fl.contract_owner_id = %(company)s )
                                     THEN fl.amount_value 
                                 ELSE 0 
                                 END 
                     )                     AS fixed_costs
        
                    
              FROM financial_ledger fl

              WHERE fl.organization_id = %(org)s
                AND fl.record_date >= %(start)s
                AND fl.record_date < %(end)s
                AND (
                  fl.buyer_id = %(company)s
                      OR fl.seller_id = %(company)s
                  )

              GROUP BY month
              ORDER BY month DESC 
              """

        conn = self._get_connection()

        try:
            with conn.cursor(dictionary=True) as cur:

                params = {
                    "org": str(organization_id),
                    "company": str(company_id),
                    "start": year_start,
                    "end": year_end,
                }

                cur.execute(sql, params)
                rows = cur.fetchall()

        finally:
            self._maybe_close(conn)

        months: list[CompanyDashboardMonthRaw] = []

        year_revenue = Decimal("0")
        year_costs = Decimal("0")
        year_non_deductible = Decimal("0")
        year_fixed_costs = Decimal("0")

        for r in rows:

            month = int(r["month"])

            revenue = r["revenue"] or Decimal("0")
            costs = r["costs"] or Decimal("0")
            non_deductible = r["non_deductible"] or Decimal("0")
            fixed_costs = r["fixed_costs"] or Decimal("0")
            internal_revenue = r["internal_revenue"] or Decimal("0")
            revenue+=internal_revenue
            internal_cost = r["internal_cost"] or Decimal("0")
            costs += internal_cost

            year_revenue += revenue
            year_costs += costs
            year_non_deductible += non_deductible
            year_fixed_costs += fixed_costs

            months.append(
                CompanyDashboardMonthRaw(
                    month=month,
                    label=MONTH_NAMES[month] if month else "",
                    revenue=revenue,
                    costs=costs,
                    non_deductible=non_deductible,
                    fixed_costs=fixed_costs,
                )
            )

        return CompanyDashboardRawData(
            year_revenue=year_revenue,
            year_costs=year_costs,
            year_non_deductible=year_non_deductible,
            year_fixed_costs=year_fixed_costs,
            months=months,
        )

    def fetch_month_breakdown(
            self,
            *,
            organization_id: UUID,
            company_id: UUID,
            year: int,
            month: int,
    ) -> list[CompanyMonthBreakdownRaw]:

        start, end = _period_range(year, month)

        sql = """
              SELECT fl.value_type_id, 
                     fl.value_type_code, 
                     fl.value_type_name, 

                    SUM(
                        CASE
                            WHEN fl.direction = 'REVENUE'
                            OR (
                                fl.direction = 'INTERNAL'
                                AND fl.seller_id = %(company)s
                            )
                            THEN fl.amount_value
                            ELSE 0
                        END
                    ) AS revenue,

                     SUM(
                        CASE
                            WHEN (
                                fl.direction = 'COST'
                                OR fl.direction = 'FIXED'
                                OR (
                                    fl.direction = 'INTERNAL'
                                    AND fl.buyer_id = %(company)s
                                )
                            )
                            AND fl.tax_treatment = 'tax_deductible'
                            THEN fl.amount_value
                            ELSE 0
                        END
                    ) AS costs,

                     SUM( 
                             CASE 
                                 WHEN fl.direction = 'COST' 
                                     AND fl.tax_treatment = 'non_deductible' 
                                     THEN fl.amount_value 
                                 ELSE 0 
                                 END 
                     ) AS non_deductible

              FROM financial_ledger fl

              WHERE fl.organization_id = %(org)s
                AND fl.record_date >= %(start)s
                AND fl.record_date < %(end)s
                AND (
                  fl.buyer_id = %(company)s
                      OR fl.seller_id = %(company)s
                  )

              GROUP BY fl.value_type_id, 
                       fl.value_type_code, 
                       fl.value_type_name

              ORDER BY costs DESC 
              """

        conn = self._get_connection()

        try:
            with conn.cursor(dictionary=True) as cur:

                params = {
                    "org": str(organization_id),
                    "company": str(company_id),
                    "start": start,
                    "end": end,
                }

                cur.execute(sql, params)
                rows = cur.fetchall()

        finally:
            self._maybe_close(conn)

        result: list[CompanyMonthBreakdownRaw] = []

        for r in rows:
            result.append(
                CompanyMonthBreakdownRaw(
                    value_type_id=r["value_type_id"],
                    code=r["value_type_code"],
                    name=r["value_type_name"],
                    revenue=r["revenue"] or Decimal("0"),
                    costs=r["costs"] or Decimal("0"),
                    non_deductible=r["non_deductible"] or Decimal("0"),
                )
            )

        return result

    def fetch_fixed_costs(
            self,
            *,
            organization_id: UUID,
            company_id: UUID,
            year: int,
            month: int | None,
    ) -> list[CompanyFixedCostRaw]:

        start, end = _period_range(year, month)

        sql = """
              SELECT fl.record_id, 
                     fl.record_date, 

    

                     fl.value_type_code, 
                     fl.value_type_name, 
                    
                    fl.item_name,
                     fl.description, 
                     fl.amount_value AS amount, 
                     fl.tax_treatment

              FROM financial_ledger fl

              WHERE fl.organization_id = %(org)s
                        AND
                  (
                     ( fl.direction = 'FIXED'
                      AND (
                            fl.buyer_id = %(company)s
                            OR fl.seller_id = %(company)s
                          )
                     )
                    OR (fl.contract_type = 'system'    -- LEGACY: remove after migration to direction=FIXED
                    AND fl.contract_owner_id = %(company)s)
                  )
                    
                    AND fl.record_date >= %(start)s
                    AND fl.record_date < %(end)s
                    ORDER BY fl.record_date DESC
              """

        conn = self._get_connection()

        try:
            with conn.cursor(dictionary=True) as cur:

                params = {
                    "org": str(organization_id),
                    "company": str(company_id),
                    "start": start,
                    "end": end,
                }

                cur.execute(sql, params)
                rows = cur.fetchall()

        finally:
            self._maybe_close(conn)

        result: list[CompanyFixedCostRaw] = []

        for r in rows:
            result.append(
                CompanyFixedCostRaw(
                    record_id=r["record_id"],
                    record_date=r["record_date"],
                    # contract_id=r["contract_id"],
                    # contract_code=r["contract_code"],
                    value_type_code=r["value_type_code"],
                    value_type_name=r["value_type_name"],
                    item_name=r["item_name"],
                    description=r["description"],
                    amount=r["amount"] or Decimal("0"),
                    tax_treatment=r["tax_treatment"],
                )
            )

        return result

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

