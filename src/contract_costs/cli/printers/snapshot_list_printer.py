def print_snapshot_list(rows):
    if not rows:
        print("No snapshots found.")
        return

    print()
    print(
        f"{'SNAPSHOT':<10}"
        f"{'DATE':<12}"
        f"{'CONTRACT':<12}"
        f"{'BUDGET':>14}"
        f"{'PROG':>7}"
        f"{'DONE':>12}"
        f"{'NET':>12}"
        f"{'NON-DEDUCT':>12}"
        f"{'SPEND':>12}"
        f"{'RESULT':>12}"
        f"{'REV':>12}"
    )
    print("-" * 125)

    for r in rows:
        done = r.planned_budget * r.progress
        spend = r.net_cost + r.non_deductible
        result = done - spend

        print(
            f"{str(r.snapshot_id)[:8]:<10}"
            f"{r.snapshot_date:%Y-%m-%d}  "
            f"{r.contract_code:<12}"
            f"{_fmt_money(r.planned_budget):>14}"
            f"{_fmt_percent(r.progress):>7}"
            f"{_fmt_money(done):>12}"
            f"{_fmt_money(r.net_cost):>12}"
            f"{_fmt_money(r.non_deductible):>12}"
            f"{_fmt_money(spend):>12}"
            f"{_fmt_money(result):>12}"
            f"{_fmt_money(r.revenue):>12}"
        )

    print()



def _fmt_money(value) -> str:
    return f"{value:,.2f}".replace(",", " ")


def _fmt_percent(value) -> str:
    return f"{value * 100:5.1f}%"

