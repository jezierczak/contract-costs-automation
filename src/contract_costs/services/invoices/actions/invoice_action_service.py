from typing import Any
from uuid import UUID

from contract_costs.model.invoice import PaymentStatus, Invoice, InvoiceStatus
from contract_costs.repository.invoice_repository import InvoiceRepository
from contract_costs.services.invoices.actions.dto.invoice_action_command import InvoiceActionCommand, InvoiceAction
from contract_costs.services.invoices.actions.invoice_selector_resolver import InvoiceSelectorResolver


class InvoiceActionService:
    def __init__(self, invoice_repository: InvoiceRepository):
        self._invoice_repo =invoice_repository
        self._invoice_selector_resolver = InvoiceSelectorResolver(self._invoice_repo)

    def execute(self, cmd: InvoiceActionCommand) -> None:
        invoice_ids = self._invoice_selector_resolver.resolve(cmd.selectors)

        match cmd.action:
            case InvoiceAction.MARK_PAID:
                self._mark_paid(invoice_ids, cmd.payload)

            case InvoiceAction.MARK_SENT_TO_ACCOUNTANT:
                self._mark_sent_to_accountant(invoice_ids)

            case InvoiceAction.MARK_UNPAID:
                self._mark_unpaid(invoice_ids)

            case InvoiceAction.REOPEN:
                self._reopen(invoice_ids)

            case _:
                raise NotImplementedError(f"Action {cmd.action} not implemented")

    def _mark_paid(
        self,
        invoice_ids: list[UUID],
        payload: dict[str, Any] | None,
    ) -> None:

        paid_at = None
        if payload:
            paid_at = payload.get("paid_at")

        for invoice_id in invoice_ids:
            invoice = self._require_invoice(invoice_id)

            if invoice.payment_status == PaymentStatus.PAID:
                continue  # albo raise, zależnie od filozofii

            updated = invoice.mark_paid(paid_at=paid_at)
            self._invoice_repo.update(updated)

    def _mark_sent_to_accountant(self, invoice_ids: list[UUID]) -> None:
        for invoice_id in invoice_ids:
            invoice = self._require_invoice(invoice_id)

            if invoice.status != InvoiceStatus.PROCESSED:
                raise ValueError(
                    f"Invoice {invoice.invoice_number} "
                    f"cannot be sent to accountant from status {invoice.status}"
                )

            updated = invoice.mark_sent_to_accountant()
            self._invoice_repo.update(updated)

    def _mark_unpaid(self, invoice_ids: list[UUID]) -> None:
        for invoice_id in invoice_ids:
            invoice = self._require_invoice(invoice_id)

            if invoice.payment_status == PaymentStatus.UNPAID:
                continue

            updated = invoice.mark_unpaid()
            self._invoice_repo.update(updated)


    def _reopen(self, invoice_ids: list[UUID]) -> None:
        for invoice_id in invoice_ids:
            invoice = self._require_invoice(invoice_id)

            if invoice.status != InvoiceStatus.SENT_TO_ACCOUNTANT:
                raise ValueError(
                    f"Invoice {invoice.invoice_number} is not closed"
                )

            updated = invoice.reopen()
            self._invoice_repo.update(updated)



    def _require_invoice(self, invoice_id: UUID) -> Invoice:
        invoice = self._invoice_repo.get(invoice_id)
        if not invoice:
            raise ValueError(f"Invoice with id {invoice_id} not found")
        return invoice