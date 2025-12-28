import pandas as pd


class ContractReportAggregator:
    BASE_GROUP = [
        "contract_id",
        "contract_code",
        "contract_name",
    ]

    METRICS = {
        "net_amount": "sum",
        "vat_amount": "sum",
        "gross_amount": "sum",
        "non_tax_amount":"sum",
        "quantity": "sum",
    }

    def aggregate(
        self,
        df: pd.DataFrame,
        *,
        group_by: list[str],
    ) -> pd.DataFrame:
        if df.empty:
            return df

        groups = self.BASE_GROUP + group_by
        # 🔥 jeżeli grupujemy po cost_node, dołącz budżet
        if "cost_node_code" in groups and "cost_node_budget" not in groups:
            groups.append("cost_node_budget")

        return (
            df
            .groupby(groups, dropna=False)
            .agg(self.METRICS)
            .reset_index()
        )
