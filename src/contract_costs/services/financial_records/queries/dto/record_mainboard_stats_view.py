from dataclasses import dataclass


@dataclass
class RecordMainboardStatsView:
    assign: int
    to_accountant: int
    unpaid_costs: int
    unpaid_revenue: int