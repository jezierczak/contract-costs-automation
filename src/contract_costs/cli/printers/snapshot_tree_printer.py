from decimal import Decimal


from collections import defaultdict


def print_snapshot_tree(nodes):
    if not nodes:
        print("No data.")
        return

    nodes_by_id = {n.node_id: n for n in nodes}
    children_by_parent = defaultdict(list)

    for n in nodes:
        children_by_parent[n.parent_id].append(n)

    for lst in children_by_parent.values():
        lst.sort(key=lambda n: n.code)

    print()
    print(
        f"{'CODE':<35}"
        f"{'BUDGET':>12}"
        f"{'PROG':>7}"
        f"{'DONE':>12}"
        f"{'NET':>12}"
        f"{'NON-DEDUCT':>12}"
        f"{'SPEND':>12}"
        f"{'RESULT':>12}"
        f"{'REV':>12}  "
        f"NAME"
    )
    print("-" * 120)

    def walk(node, prefix: str, is_last: bool):
        connector = "└── " if is_last else "├── "
        code = f"{prefix}{connector}{node.code}" if prefix else node.code

        done = node.planned_budget * node.progress
        spend = node.net + node.non_deductible
        result = done - spend

        print(
            f"{code:<35}"
            f"{_fmt_money(node.planned_budget):>12}"
            f"{_fmt_percent(node.progress):>7}"
            f"{_fmt_money(done):>12}"
            f"{_fmt_money(node.net):>12}"
            f"{_fmt_money(node.non_deductible):>12}"
            f"{_fmt_money(spend):>12}"
            f"{_fmt_money(result):>12}"
            f"{_fmt_money(getattr(node, 'revenue', Decimal('0'))):>12}  "
            f"{node.name}"
        )

        new_prefix = prefix + ("    " if is_last else "│   ")
        children = children_by_parent.get(node.node_id, [])

        for idx, child in enumerate(children):
            walk(child, new_prefix, idx == len(children) - 1)

    roots = children_by_parent[None]
    for idx, root in enumerate(roots):
        walk(root, "", idx == len(roots) - 1)

    print()


def _fmt_money(value: Decimal) -> str:
    return f"{value:,.2f}".replace(",", " ")


def _fmt_percent(value: Decimal) -> str:
    return f"{(value * 100):.1f} %"

