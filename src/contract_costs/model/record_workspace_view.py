from enum import Enum


class RecordWorkspaceView(str, Enum):
    ALL = "all"
    ASSIGN = "assign"
    TO_ACCOUNTANT = "to_accountant"
    UNPAID_COSTS = "unpaid_costs"
    UNPAID_REVENUE = "unpaid_revenue"