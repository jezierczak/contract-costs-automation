import logging
from dataclasses import replace
from datetime import datetime
from uuid import uuid4

from contract_costs.model.invoice import Invoice, InvoiceStatus
from contract_costs.services.invoices.assigment.apply.commands.invoice_command import InvoiceCommand
from contract_costs.services.invoices.assigment.ingest.completion_validator.invoice_completion_validator import \
    InvoiceCompletionValidator
from contract_costs.services.invoices.assigment.ingest.dto.invoice_ref_result import (
    InvoiceRefResult,
    InvoiceApplyAction,
)
from contract_costs.services.invoices.assigment.invoice_sources.dto.common import ResolvedInvoiceUpdate
from contract_costs.services.invoices.assigment.ingest.invoice_ingest_service import InvoiceIngestService

logger = logging.getLogger(__name__)


class ExcelInvoiceIngestService(InvoiceIngestService):
    """
    Excel ingest:
    - source of truth
    - APPLY / MODIFY / DELETE
    - obsługuje old_invoice_number
    - respektuje workflow
    """

    def apply(
        self,
        updates: list[ResolvedInvoiceUpdate],
    ) -> dict[str, InvoiceRefResult]:

        results: dict[str, InvoiceRefResult] = {}

        for update in updates:
            if not update.invoice_number or not update.invoice_number.strip():
                raise ValueError("Excel ingest requires invoice_number")

            ref_key = update.invoice_number

            if ref_key in results:
                raise ValueError(f"Duplicate invoice reference in batch: {ref_key}")

            existing = self._get_existing_invoice(update)

            buyer = update.buyer
            seller = update.seller
            # update_direction = self.resolve_direction(buyer,seller)

            # -------------------------------------------------
            # SKIP FINALIZED
            # -------------------------------------------------
            if existing and existing.status in {
                InvoiceStatus.PROCESSED,
                InvoiceStatus.SENT_TO_ACCOUNTANT,
            }:
                logger.warning(
                    "Skipping finalized invoice %s",
                    existing.invoice_number,
                )
                results[ref_key] = InvoiceRefResult(
                    invoice_id=existing.id,
                    action=InvoiceApplyAction.SKIPPED,
                    invoice_number=existing.invoice_number,
                    old_invoice_number=update.old_invoice_number,
                    buyer_role=buyer.role,
                    seller_role=seller.role

                )
                continue

            # -------------------------------------------------
            # DELETE (LOGICAL)
            # -------------------------------------------------
            if update.command == InvoiceCommand.DELETE:
                if existing is None:
                    results[ref_key] = InvoiceRefResult(
                        invoice_id=None,
                        action=InvoiceApplyAction.SKIPPED,
                        invoice_number=update.invoice_number,
                        old_invoice_number=update.old_invoice_number,
                        buyer_role=buyer.role,
                        seller_role=seller.role
                    )
                    continue

                self._invoice_repository.update(
                    replace(existing, status=InvoiceStatus.DELETED)
                )

                results[ref_key] = InvoiceRefResult(
                    invoice_id=existing.id,
                    action=InvoiceApplyAction.DELETED,
                    invoice_number=existing.invoice_number,
                    old_invoice_number=update.old_invoice_number,
                    buyer_role=buyer.role,
                    seller_role=seller.role
                )
                continue

            # -------------------------------------------------
            # BUSINESS RULE:
            # At least one side (buyer or seller) must be OWN
            # for APPLY / CREATE operations
            # -------------------------------------------------
            if not InvoiceCompletionValidator.resolve_invoice_direction(buyer.role,seller.role):
                raise RuntimeError(
                    f"Invoice {update.invoice_number} has no OWN company "
                    f"(buyer={buyer.tax_number}, seller={seller.tax_number})"
                )

            # -------------------------------------------------
            # APPLY / MODIFY
            # -------------------------------------------------
            if existing:
                updated = replace(
                    existing,
                    invoice_number=update.invoice_number,
                    invoice_date=update.invoice_date,
                    selling_date=update.selling_date,
                    buyer_id=update.buyer.id,
                    seller_id=update.seller.id,
                    payment_method=update.payment_method,
                    due_date=update.due_date,
                    paid_date=update.paid_date,
                    payment_status=update.payment_status,
                    status=update.status,
                    tags=self._resolve_tags(update.tags),
                    scan_filename=update.scan_filename,
                )
                self._invoice_repository.update(updated)

                results[ref_key] = InvoiceRefResult(
                    invoice_id=existing.id,
                    action=InvoiceApplyAction.APPLIED,
                    invoice_number=update.invoice_number,
                    old_invoice_number=update.old_invoice_number,
                    buyer_role=buyer.role,
                    seller_role=seller.role
                )
                continue

            # -------------------------------------------------
            # CREATE
            # -------------------------------------------------
            invoice_id = uuid4()
            invoice = Invoice(
                id=invoice_id,
                invoice_number=update.invoice_number,
                invoice_date=update.invoice_date,
                selling_date=update.selling_date,
                buyer_id=update.buyer.id,
                seller_id=update.seller.id,
                payment_method=update.payment_method,
                due_date=update.due_date,
                paid_date=update.paid_date,
                payment_status=update.payment_status,
                status=update.status,
                timestamp=datetime.now(),
                tags=self._resolve_tags(update.tags),
                scan_filename=update.scan_filename,
            )

            self._invoice_repository.add(invoice)

            # -------------------------------------------------
            # OLD INVOICE NUMBER → logical delete
            # -------------------------------------------------
            # LEGACY:
            # old_invoice_number logic was used when invoice_number
            # was the primary identity (pre invoice_id refactor).
            # Kept temporarily for safety during transition.

            # if update.old_invoice_number and update.old_invoice_number != update.invoice_number:
            #     candidates = self._invoice_repository.get_for_assignment(
            #         InvoiceStatus.IN_PROGRESS
            #     )
            #
            #     old = next(
            #         (c for c in candidates if c.invoice_number == update.old_invoice_number),
            #         None,
            #     )
            #
            #     if old is None:
            #         raise ValueError(
            #             f"Old invoice not found in IN_PROGRESS: {update.old_invoice_number}"
            #         )
            #
            #     self._invoice_repository.update(
            #         replace(old, status=InvoiceStatus.DELETED)
            #     )

            results[ref_key] = InvoiceRefResult(
                invoice_id=invoice_id,
                action=InvoiceApplyAction.APPLIED,
                invoice_number=invoice.invoice_number,
                old_invoice_number=update.old_invoice_number,
                buyer_role=buyer.role,
                seller_role=seller.role
            )

        return results
