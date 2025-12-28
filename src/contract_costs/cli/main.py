import argparse
import logging
import os
import sys

from contract_costs.cli.commands.add_company import handle_add_company
from contract_costs.cli.commands.apply_excel_contract import handle_applyexcel_contract
from contract_costs.cli.commands.apply_excel_invoices import handle_applyexcel_invoices
from contract_costs.cli.commands.edit_company import handle_edit_company
from contract_costs.cli.commands.add_cost_type import handle_add_cost_type
from contract_costs.cli.commands.add_contract import handle_add_contract
from contract_costs.cli.commands.init import handle_init
from contract_costs.cli.commands.report import register_report_commands
from contract_costs.cli.commands.run import handle_run
from contract_costs.cli.commands.showexcel_contract import handle_showexcel_contract
from contract_costs.cli.commands.showexcel_invoices import handle_showexcel_invoices

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def log_unhandled_exception(exc_type, exc, tb):
    logging.critical(
        "UNHANDLED EXCEPTION",
        exc_info=(exc_type, exc, tb),
    )

sys.excepthook = log_unhandled_exception

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="contract-costs",
        description="Contract costs management CLI",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    register_report_commands(subparsers)

    subparsers.add_parser("init", help="Initialize application environment")
    subparsers.add_parser("run", help="Run invoice watcher")

    # ---- add ----
    add_parser = subparsers.add_parser("add", help="Add new entity")
    add_sub = add_parser.add_subparsers(dest="entity", required=True)

    add_sub.add_parser("company", help="Add company")
    add_sub.add_parser("contract", help="Add contract")
    add_sub.add_parser("cost-type", help="Add cost type")

    # ---- edit (placeholder) ----
    edit_parser = subparsers.add_parser("edit", help="Edit existing entity")
    edit_sub = edit_parser.add_subparsers(dest="entity", required=True)

    edit_sub.add_parser("company", help="Edit existing companies")

    showexcel_parser = subparsers.add_parser("showexcel")
    showexcel_sub = showexcel_parser.add_subparsers(dest="entity")

    showexcel_contract_parser = showexcel_sub.add_parser("contract")
    showexcel_contract_parser.add_argument(
        "contract_ref",
        nargs="?",
        help="Contract UUID or code",
    )

    showexcel_invoice_parser = showexcel_sub.add_parser("invoices")
    showexcel_invoice_parser.add_argument(
        "mode",
        nargs="?",
        help="Show invoice status new, in_progress, for both",
    )

    applyexcel_parser = subparsers.add_parser("applyexcel")
    applyexcel_sub = applyexcel_parser.add_subparsers(dest="entity")

    applyexcel_sub_contract_parser = applyexcel_sub.add_parser("contract")
    applyexcel_sub_contract_parser.add_argument(
        "contract_ref",
        nargs="?",
        help="new from New, or Contract UUID or code from Edit",
    )

    applyexcel_sub_invoice_parser = applyexcel_sub.add_parser("invoices")
    applyexcel_sub_invoice_parser.add_argument(
        "file",
        nargs="?",
        help="Path to invoices excel file",
    )

    return parser


def main(argv: list[str] | None = None) -> None:
    import contract_costs.config as cfg  # 🔥 JAWNE: config ładuje się TU
    logging.info("APP_ENV=%s | WORK_DIR=%s | DB=%s",
                 cfg.APP_ENV, cfg.WORK_DIR, cfg.DB_CONFIG["database"])

    if os.getenv("APP_ENV", "test") == "prod":
        print("⚠️  RUNNING IN PRODUCTION MODE ⚠️")
        confirm = input("Type 'PROD' to continue: ")
        if confirm != "PROD":
            print("Aborted.")
            exit(1)

    parser = build_parser()
    args = parser.parse_args(argv)

    # ---------- ROUTING ----------

    if hasattr(args, "handler"):
        args.handler(args)
        return

    if args.command == "init":
        handle_init()
        return

    if args.command == "run":
        handle_run()
        return

    if args.command == "add" and args.entity == "company":
        handle_add_company()
        return

    if args.command == "add" and args.entity == "contract":
        handle_add_contract()
        return

    if args.command == "add" and args.entity == "cost-type":
        handle_add_cost_type()
        return

    if args.command == "edit" and args.entity == "company":
        handle_edit_company()
        return

    if args.command == "showexcel" and args.entity == "contract":
        handle_showexcel_contract(args.contract_ref)
        return

    if args.command == "showexcel" and args.entity == "invoices":
        handle_showexcel_invoices(args.mode)
        return

    if args.command == "applyexcel" and args.entity == "contract":
        handle_applyexcel_contract(args.contract_ref)
        return

    if args.command == "applyexcel" and args.entity == "invoices":
        handle_applyexcel_invoices(args.file)
        return


    # fallback (nie powinno się zdarzyć)
    parser.print_help()


if __name__ == "__main__":
    main(sys.argv[1:])
