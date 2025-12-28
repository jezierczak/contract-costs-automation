GROUP_BY_MAP = {
    "cost_node": "cost_node_code",
    "cost_type": "cost_type_code",
    "invoice": "invoice_number",
    "invoice_date": "invoice_date",
}

def resolve_grouping(cli_groups: list[str]) -> list[str]:
    cols = []
    for g in cli_groups:
        if g not in GROUP_BY_MAP:
            raise ValueError(f"Unknown grouping: {g}")
        cols.append(GROUP_BY_MAP[g])
    return cols
