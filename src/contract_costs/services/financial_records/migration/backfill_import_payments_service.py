from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.common.time import local_today
from contract_costs.model.financial_record import (
    FinancialRecord,
    FinancialRecordStatus,
    PaymentMethod,
    PaymentStatus,
    SETTLED_AT_SALE_PAYMENT_METHODS,
)
from contract_costs.services.financial_records.actions.dto.invoice_action_command import (
    FinancialRecordAction,
    FinancialRecordActionCommand,
    FinancialRecordSelector,
)
from contract_costs.services.financial_records.actions.financial_record_action_service import (
    FinancialRecordActionService,
)
from contract_costs.services.financial_records.migration.backfill_import_payments_command import (
    BackfillImportPaymentsCommand,
)
from contract_costs.unit_of_work import UnitOfWork


@dataclass(frozen=True, slots=True)
class ImportPaymentFix:
    record_id: UUID
    reference: str
    invoice_date: date | None
    payment_method: PaymentMethod
    payment_status: PaymentStatus
    payable: Decimal
    already_paid: Decimal
    paid_date: date

    @property
    def missing(self) -> Decimal:
        return max(self.payable - self.already_paid, Decimal("0"))


class BackfillImportPaymentsService(
    ActionHandler[BackfillImportPaymentsCommand, list[ImportPaymentFix]]
):
    """
    Naprawa rekordów sprzed reguły „gotówka/karta/BLIK/bon/przedpłata = zapłacone”
    i sprzed zapisywania wpłaty przy imporcie:
    - forma płatności z SETTLED_AT_SALE_PAYMENT_METHODS, ale status inny niż PAID,
    - status PAID bez wpłat (lub z wpłatami poniżej kwoty do zapłaty).
    Bez `apply` tylko zwraca listę; z `apply` dopłaca brakującą kwotę akcją MARK_PAID.
    """

    def __init__(self, action_service: FinancialRecordActionService) -> None:
        self._actions = action_service

    def execute(
        self,
        *,
        action: BackfillImportPaymentsCommand,
        uow: UnitOfWork,
    ) -> list[ImportPaymentFix]:
        fixes = [
            fix
            for record in uow.financial_records.list_all(organization_id=action.organization_id)
            if (fix := self._fix_for(uow=uow, record=record)) is not None
        ]

        if action.apply:
            for fix in fixes:
                self._actions.execute(
                    action=FinancialRecordActionCommand(
                        organization_id=action.organization_id,
                        actor_user_id=action.actor_user_id,
                        action=FinancialRecordAction.MARK_PAID,
                        selectors=[FinancialRecordSelector(record_id=fix.record_id)],
                        payload={"paid_date": fix.paid_date},
                    ),
                    uow=uow,
                )

        return fixes

    @staticmethod
    def _fix_for(*, uow: UnitOfWork, record: FinancialRecord) -> ImportPaymentFix | None:
        if record.status == FinancialRecordStatus.DELETED:
            return None

        settled_at_sale = record.payment_method in SETTLED_AT_SALE_PAYMENT_METHODS
        if not settled_at_sale and record.payment_status != PaymentStatus.PAID:
            return None

        lines = uow.financial_record_lines.list_by_financial_record(
            organization_id=record.organization_id, financial_record_id=record.id,
        )
        payments = uow.financial_record_payments.list_by_financial_record(
            organization_id=record.organization_id, financial_record_id=record.id,
        )
        payable = sum((line.amount.payable for line in lines), Decimal("0"))
        already_paid = sum((p.amount for p in payments), Decimal("0"))

        if payable > 0:
            needs_fix = already_paid < payable
        else:
            needs_fix = record.payment_status != PaymentStatus.PAID

        if not needs_fix:
            return None

        return ImportPaymentFix(
            record_id=record.id,
            reference=record.reference,
            invoice_date=record.invoice_date,
            payment_method=record.payment_method,
            payment_status=record.payment_status,
            payable=payable,
            already_paid=already_paid,
            paid_date=record.paid_date or record.invoice_date or local_today(),
        )
