from uuid import UUID

from contract_costs.cli.context import get_services
from contract_costs.services.invoices.actions.dto.invoice_action_command import (
    InvoiceActionCommand,
    InvoiceAction, InvoiceSelector,
)

from contract_costs.cli.registry import REGISTRY


def build_set_invoice(subparsers):
    p = subparsers.add_parser(
        "invoice",
        help="Set invoice state",
    )

    p.add_argument(
        "action",
        choices=["paid", "unpaid", "sent-to-accountant", "reopen"],
        help="Action (paid, unpaid, sent-to-accountant, reopen)",
    )

    p.add_argument(
        "ref",
        help="Invoice UUID or invoice number",
    )

    p.set_defaults(handler=handle_set_invoice)

REGISTRY.register_group("set", build_set_invoice)
ACTION_MAP = {
    "paid": InvoiceAction.MARK_PAID,
    "unpaid": InvoiceAction.MARK_UNPAID,
    "sent-to-accountant": InvoiceAction.MARK_SENT_TO_ACCOUNTANT,
    "reopen": InvoiceAction.REOPEN,
}

def handle_set_invoice(args) -> None:
    services = get_services()

    try:
        action = ACTION_MAP[args.action]
    except KeyError:
        print(f"Invalid action: {args.action}")
        print("Allowed:", ", ".join(a.name.lower() for a in InvoiceAction))
        return

    try:
        selector = InvoiceSelector(invoice_id=UUID(args.ref))
    except ValueError:
        selector = InvoiceSelector(invoice_number=args.ref)

    cmd = InvoiceActionCommand(
        action=action,
        selectors=[selector],
    )

    services.invoice_action_service.execute(cmd)

    print(f"✔ Invoice {args.ref} → {action.value}")


