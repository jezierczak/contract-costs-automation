import logging
from dataclasses import replace
from datetime import datetime
from uuid import uuid4

from contract_costs.model.invoice import Invoice, InvoiceStatus
from contract_costs.services.invoices.assigment.ingest.dto.invoice_ref_result import (
    InvoiceRefResult,
    InvoiceApplyAction,
)
from contract_costs.services.invoices.assigment.invoice_sources.dto.common import ResolvedInvoiceUpdate
from contract_costs.services.invoices.assigment.ingest.invoice_ingest_service import InvoiceIngestService

logger = logging.getLogger(__name__)


class PdfInvoiceIngestService(InvoiceIngestService):
    """
    PDF ingest:
    - nie ufa numerom faktur
    - wykrywa kolizje OCR
    - nigdy nie DELETE
    - nigdy nie PROCESSED
    """

    def apply(
        self,
        updates: list[ResolvedInvoiceUpdate],
    ) -> dict[str, InvoiceRefResult]:

        results: dict[str, InvoiceRefResult] = {}

        for update in updates:
            if not update.invoice_number or not update.invoice_number.strip():
                raise ValueError("PDF ingest requires invoice_number (even placeholder)")

            existing = self._get_existing_invoice(update)

            # -------------------------------------------------
            # OCR COLLISION → suffix -duplicate
            # -------------------------------------------------
            if existing is not None:
                logger.warning(
                    "OCR collision detected for invoice %s → creating duplicate",
                    update.invoice_number,
                )

                update = replace(
                    update,
                    invoice_number=f"{update.invoice_number}-duplicate",
                )


            ref_key = update.invoice_number

            if ref_key in results:
                raise ValueError(f"Duplicate invoice reference in batch: {ref_key}")
            """
            PDF ingest assumes all updates are APPLY.
            DELETE / MODIFY are not part of this ingest contract.
            """
            # -------------------------------------------------
            # CREATE ONLY (PDF does not MODIFY existing)
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
                status=update.status or InvoiceStatus.NEW_COST,
                timestamp=datetime.now(),
                tags=self._resolve_tags(update.tags),
                scan_filename=update.scan_filename,
            )

            self._invoice_repository.add(invoice)

            results[ref_key] = InvoiceRefResult(
                invoice_id=invoice_id,
                action=InvoiceApplyAction.APPLIED,
                invoice_number=invoice.invoice_number,
                old_invoice_number=update.old_invoice_number,
            )

        return results
