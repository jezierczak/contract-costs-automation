import pandas as pd
import pytest

from contract_costs.services.reports.aggregator import ContractReportAggregator
from contract_costs.services.reports.grouping import resolve_grouping


def test_resolve_grouping_maps_cli_names() -> None:
    assert resolve_grouping(["cost_node", "invoice"]) == [
        "cost_node_code",
        "invoice_number",
    ]


def test_resolve_grouping_rejects_unknown_group() -> None:
    with pytest.raises(ValueError, match="Unknown grouping"):
        resolve_grouping(["bad_group"])


def test_contract_report_aggregator_returns_empty_df_as_is() -> None:
    agg = ContractReportAggregator()
    empty = pd.DataFrame()

    result = agg.aggregate(empty, group_by=["cost_type_code"])

    assert result.empty


def test_contract_report_aggregator_adds_earned_for_cost_node_grouping() -> None:
    agg = ContractReportAggregator()
    metrics_snapshot = dict(agg.METRICS)
    try:
        df = pd.DataFrame(
            [
                {
                    "contract_code": "C1",
                    "cost_node_code": "N1",
                    "cost_node_name": "Node 1",
                    "cost_node_budget": 1000.0,
                    "net_amount": 100.0,
                    "vat_amount": 23.0,
                    "gross_amount": 123.0,
                    "non_tax_amount": 0.0,
                    "total": 123.0,
                },
                {
                    "contract_code": "C1",
                    "cost_node_code": "N1",
                    "cost_node_name": "Node 1",
                    "cost_node_budget": 1000.0,
                    "net_amount": 50.0,
                    "vat_amount": 11.5,
                    "gross_amount": 61.5,
                    "non_tax_amount": 0.0,
                    "total": 61.5,
                },
            ]
        )

        result = agg.aggregate(df, group_by=["cost_node_code"])

        assert len(result) == 1
        row = result.iloc[0]
        assert row["total"] == 184.5
        assert row["earned"] == 815.5
        assert row["cost_node_budget"] == 1000.0
    finally:
        agg.METRICS = metrics_snapshot

