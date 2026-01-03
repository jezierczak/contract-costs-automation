import pandas as pd


class ContractReportAggregator:
    BASE_GROUP = [
        # "contract_id",
        "contract_code",
        # "contract_name",
    ]

    METRICS = {
        "net_amount": "sum",
        "vat_amount": "sum",
        "gross_amount": "sum",
        "non_tax_amount":"sum",
        # "quantity": "sum",
        "total": "sum",
        # "earned": "first",
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
        if "cost_node_code" in groups:
            groups += ["cost_node_name"]

            total_per_node = (
                df.groupby("cost_node_code")["total"]
                .transform("sum")
            )

            df["earned"] = df["cost_node_budget"] - total_per_node
            if "earned" not in self.METRICS:
                self.METRICS["earned"] = "first"
            if "cost_node_budget" not in self.METRICS:
                self.METRICS["cost_node_budget"] = "first"




        return (
            df
            .groupby(groups, dropna=False)
            .agg(self.METRICS)
            .reset_index()
        )
