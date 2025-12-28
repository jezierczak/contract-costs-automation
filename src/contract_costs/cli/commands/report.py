from contract_costs.cli.commands.reports.report_costs import handle_report_costs


def register_report_commands(subparsers):
    report_parser = subparsers.add_parser(
        "report",
        help="Generate reports",
    )

    report_sub = report_parser.add_subparsers(
        dest="report_type",
        required=True,
    )

    # ---------- report costs ----------
    costs = report_sub.add_parser(
        "costs",
        help="Contract cost report",
    )

    costs.add_argument(
        "contract_ref",
        help="Contract UUID or code",
    )

    costs.add_argument(
        "--group-by",
        nargs="+",
        choices=[
            "cost_node",
            "cost_type",
            "invoice",
        ],
        default=["cost_node"],
        help="Grouping fields (default: cost_node)",
    )

    costs.add_argument(
        "--output",
        choices=["stdout", "excel"],
        default="stdout",
        help="Output format",
    )

    costs.add_argument(
        "--invoice",
        nargs="+",
        help="Filter by invoice numbers",
    )

    costs.add_argument(
        "--status",
        nargs="+",
        choices=["NEW", "IN_PROGRESS","PROCESSED", "PAID","NOT_PAID", "DELETED"],
        help="Filter by invoice status",
    )

    costs.set_defaults(handler=handle_report_costs)
