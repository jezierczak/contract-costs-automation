import logging
from dataclasses import replace
from datetime import datetime
from uuid import uuid4, UUID

from contract_costs.model.invoice import Invoice, InvoiceStatus
from contract_costs.repository.invoice_repository import InvoiceRepository
from contract_costs.services.invoices.commands.invoice_command import InvoiceCommand
from contract_costs.services.invoices.dto.apply import (
    InvoiceRefResult,
    InvoiceApplyAction,
)
from contract_costs.services.invoices.dto.common import ResolvedInvoiceUpdate

logger = logging.getLogger(__name__)


class InvoiceUpdateService:
    """
    Odpowiada WYŁĄCZNIE za:
    - tworzenie faktur
    - modyfikację faktur
    - logiczne DELETE (workflow)
    """

    def __init__(self, invoice_repository: InvoiceRepository) -> None:
        self._invoice_repository = invoice_repository

    def apply(
        self,
        invoices: list[ResolvedInvoiceUpdate],
    ) -> dict[str, InvoiceRefResult]:
        """
        Zwraca mapę:
        invoice_ref (old lub new) -> InvoiceRefResult
        """
        results: dict[str, InvoiceRefResult] = {}
        for update in invoices:
            if not update.invoice_number or not update.invoice_number.strip():
                raise ValueError(
                    f"Missing invoice_number for row with seller_id={update.seller_id}"
                )

            ref_key = update.invoice_number

            if ref_key in results:
                raise ValueError(
                    f"Duplicate invoice reference in batch: {ref_key}"
                )

            existing = self._get_existing_invoice(update)

            # -----------------------------
            # SKIP PROCESSED
            # -----------------------------
            if existing and existing.status == InvoiceStatus.PROCESSED:
                results[ref_key] = InvoiceRefResult(
                    invoice_id=existing.id,
                    action=InvoiceApplyAction.SKIPPED,
                    invoice_number=existing.invoice_number,
                    old_invoice_number=update.old_invoice_number,
                )
                logger.warning(
                    "Skipping PROCESSED invoice %s",
                    existing.invoice_number,
                )
                continue

            # -----------------------------
            # DELETE (LOGICAL)
            # -----------------------------
            if update.command == InvoiceCommand.DELETE:

                if existing is None:

                    results[ref_key] = InvoiceRefResult(
                        invoice_id=None,
                        action=InvoiceApplyAction.SKIPPED,
                        invoice_number=update.invoice_number,
                        old_invoice_number=update.old_invoice_number,
                    )
                    continue


                updated = replace(
                    existing,
                    status=InvoiceStatus.DELETED,
                )
                self._invoice_repository.update(updated)

                results[ref_key] = InvoiceRefResult(
                    invoice_id=existing.id,
                    action=InvoiceApplyAction.DELETED,
                    invoice_number=existing.invoice_number,
                    old_invoice_number=update.old_invoice_number,
                )
                continue

            # -----------------------------
            # APPLY / MODIFY (same logic)
            # -----------------------------
            if existing:
                updated = replace(
                    existing,
                    invoice_number=update.invoice_number,
                    invoice_date=update.invoice_date,
                    selling_date=update.selling_date,
                    buyer_id=update.buyer_id,
                    seller_id=update.seller_id,
                    payment_method=update.payment_method,
                    due_date=update.due_date,
                    payment_status=update.payment_status,
                    status=update.status,
                )
                self._invoice_repository.update(updated)

                results[ref_key] = InvoiceRefResult(
                    invoice_id=existing.id,
                    action=InvoiceApplyAction.APPLIED,
                    invoice_number=update.invoice_number,
                    old_invoice_number=update.old_invoice_number,
                )
                continue

            # -----------------------------
            # CREATE
            # -----------------------------
            new_id = uuid4()
            invoice = Invoice(
                id=new_id,
                invoice_number=update.invoice_number,
                invoice_date=update.invoice_date,
                selling_date=update.selling_date,
                buyer_id=update.buyer_id,
                seller_id=update.seller_id,
                payment_method=update.payment_method,
                due_date=update.due_date,
                payment_status=update.payment_status,
                status=update.status,
                timestamp=datetime.now(),
            )

            self._invoice_repository.add(invoice)

            if update.old_invoice_number and update.old_invoice_number != invoice.invoice_number:
                old = None
                candidates = self._invoice_repository.get_for_assignment(
                    InvoiceStatus.IN_PROGRESS
                )

                for candidate in candidates:
                    if candidate.invoice_number == update.old_invoice_number:
                        old = candidate
                        break

                if old is None:
                    raise ValueError(
                        f"Old invoice not found in IN_PROGRESS: {update.old_invoice_number}"
                    )

                self._invoice_repository.update(
                    replace(old, status=InvoiceStatus.DELETED)
                )

            results[ref_key] = InvoiceRefResult(
                invoice_id=new_id,
                action=InvoiceApplyAction.APPLIED,
                invoice_number=invoice.invoice_number,
            )

        return results

    def _get_existing_invoice(
        self,
        update: ResolvedInvoiceUpdate,
    ) -> Invoice | None:
        ref = update.invoice_number
        return self._invoice_repository.get_unique_invoice(
            ref,
            update.seller_id,
        )

    def mark_processed(self, invoice_ids: list[UUID]) -> None:
        for inv_id in invoice_ids:
            invoice = self._invoice_repository.get(inv_id)
            if not invoice or invoice.status == InvoiceStatus.PROCESSED:
                continue

            updated = replace(invoice, status=InvoiceStatus.PROCESSED)
            self._invoice_repository.update(updated)
