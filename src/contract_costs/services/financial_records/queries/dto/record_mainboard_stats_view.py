from dataclasses import dataclass


@dataclass
class RecordMainboardStatsView:
    assign: int
    to_accountant: int
    sent_history: int
    unpaid_costs: int
    unpaid_revenue: int
    unpaid_internal: int
