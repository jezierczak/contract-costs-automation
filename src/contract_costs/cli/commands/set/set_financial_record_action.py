from uuid import UUID

from contract_costs.cli.context import get_services
from contract_costs.cli.utils.context_helpers import require_organization_id, require_user_id
from contract_costs.common.context.exceptions import ContextError
from contract_costs.services.financial_records.actions.dto.invoice_action_command import (
    FinancialRecordActionCommand,
    FinancialRecordAction, FinancialRecordSelector,
)

from contract_costs.cli.registry import REGISTRY


def build_set_financial_record(subparsers):
    p = subparsers.add_parser(
        "record",
        help="Set financial record state",
    )

    p.add_argument(
        "action",
        choices=["paid", "unpaid", "sent-to-accountant", "reopen"],
        help="Action (paid, unpaid, sent-to-accountant, reopen)",
    )

    p.add_argument(
        "ref",
        help="Financial record UUID or financial record reference",
    )

    p.set_defaults(handler=handle_set_financial_record)

REGISTRY.register_group("set", build_set_financial_record)

ACTION_MAP = {
    "paid": FinancialRecordAction.MARK_PAID,
    "unpaid": FinancialRecordAction.MARK_UNPAID,
    "sent-to-accountant": FinancialRecordAction.MARK_SENT_TO_ACCOUNTANT,
    "reopen": FinancialRecordAction.REOPEN,
}

def handle_set_financial_record(args) -> None:
    services = get_services()
    try:
        organization_id = require_organization_id(services.context)
        actor_user_id = require_user_id(services.context)
    except ContextError:
        return

    try:
        action = ACTION_MAP[args.action]
    except KeyError:
        print(f"Financial record action: {args.action}")
        print("Allowed:", ", ".join(a.name.lower() for a in FinancialRecordAction))
        return

    try:
        selector = FinancialRecordSelector(record_id=UUID(args.ref))
    except ValueError:
        selector = FinancialRecordSelector(record_reference=args.ref)

    cmd = FinancialRecordActionCommand(
        action=action,
        selectors=[selector],
        organization_id=organization_id,
        actor_user_id=actor_user_id
    )
    services.action_bus.execute(action=cmd,handler=services.financial_record_action_service)

    print(f"✔ Invoice {args.ref} → {action.value}")


