
from uuid import UUID

import pandas as pd

from contract_costs.services.reports.aggregator import ContractReportAggregator
from contract_costs.services.reports.grouping import resolve_grouping

COLUMN_ORDER = [
    "contract_code",
    "cost_node_code",
    "cost_node_name",

    "net_amount",
    "vat_amount",
    "gross_amount",
    "non_tax_amount",
    "cost_node_budget",
    "total",
    "earned",
]


DISPLAY_NAMES = {
    "contract_code": "Kontrakt",
    "cost_node_code": "Kod pozycji",
    "cost_node_name": "Nazwa pozycji",
    "cost_node_budget": "Budżet",
    "net_amount": "Netto",
    "vat_amount": "VAT",
    "gross_amount": "Brutto",
    "non_tax_amount": "Nieopodatkowane",
    "total": "Razem",
    "earned": "Wynik",
}


class ContractCostReportRunner:

    def __init__(self, row_service):
        self._row_service = row_service
        self._aggregator = ContractReportAggregator()

    def run(
            self,
            *,
            contract_id: UUID,
            group_by: list[str],
            invoice_numbers: list[str] | None = None,
            invoice_statuses: list[str] | None = None,
    ):

        rows = self._row_service.generate_rows(contract_id)

        df = pd.DataFrame(rows, )
        df["total"] =  df["non_tax_amount"] + df["net_amount"]

        if invoice_numbers:
            df = df[df["invoice_number"].isin(invoice_numbers)]

        if invoice_statuses:
            df = df[df["invoice_status"].isin(invoice_statuses)]

        groups = resolve_grouping(group_by)

        result = self._aggregator.aggregate(df, group_by=groups)

        #dodajemy kolumn liczbowych

        numeric_columns = [k for k,v in ContractReportAggregator.METRICS.items() if v!="first" ]
        derived_columns = [k for k,v in ContractReportAggregator.METRICS.items() if v=="first" ]
        #derived_columns = ["earned"]
        result[numeric_columns+derived_columns] = (
            result[numeric_columns+derived_columns]
            .apply(pd.to_numeric, errors="coerce")
            .fillna(0)
        )

        sum_row = result[numeric_columns].sum().to_frame().T

        # uzupełniamy kolumny opisowe
        for col in result.columns:
            if col not in numeric_columns:
                sum_row[col] = ""

        # etykieta w pierwszej kolumnie
        sum_row[result.columns[0]] = "SUMA"



        for col in derived_columns:
            sum_row[col] = result[col].sum()

        # zachowujemy kolejność kolumn
        sum_row = sum_row[result.columns]

        # doklejamy na dół
        result = pd.concat([result, sum_row], ignore_index=True)

        result = (
            result
            .pipe(lambda df: df[[c for c in COLUMN_ORDER if c in df.columns]])
            .rename(columns=DISPLAY_NAMES)
        )

        return result
