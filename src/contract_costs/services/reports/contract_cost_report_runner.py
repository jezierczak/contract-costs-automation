from uuid import UUID

import pandas as pd

from contract_costs.services.reports.aggregator import ContractReportAggregator
from contract_costs.services.reports.grouping import resolve_grouping


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
        df = pd.DataFrame(rows)

        if invoice_numbers:
            df = df[df["invoice_number"].isin(invoice_numbers)]

        if invoice_statuses:
            df = df[df["invoice_status"].isin(invoice_statuses)]

        groups = resolve_grouping(group_by)
        return self._aggregator.aggregate(df, group_by=groups)

