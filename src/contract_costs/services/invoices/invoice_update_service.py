import logging
from dataclasses import replace
from datetime import datetime
from uuid import uuid4, UUID

from contract_costs.model.invoice import Invoice, InvoiceStatus
from contract_costs.repository.invoice_repository import InvoiceRepository
from contract_costs.services.invoices.dto.common import InvoiceUpdate

logging.getLogger(__name__)

class InvoiceUpdateService:
    """
    Odpowiada wyłącznie za:
    - tworzenie faktur
    - aktualizację faktur
    """

    def __init__(self, invoice_repository: InvoiceRepository) -> None:
        self._invoice_repository = invoice_repository


    def apply(self, invoices: list[InvoiceUpdate]) -> dict[str,UUID]:

        """
        Zwraca mapę:
        external_ref -> wygenerowane invoice_id
        """
        ref_map: dict[str, UUID] = {}

        for update in invoices:

            if update.invoice_number in ref_map:
                logging.error(
                    "Duplicate invoice_number in batch: %s (seller conflict possible)",
                    update.invoice_number
                )
                raise ValueError("Duplicate invoice_number in batch")
            #istniejąca faktura to robimy jej update,
            invoice = self._get_existing_invoice(update)
            if invoice is not None:
                ref_map[invoice.invoice_number] = invoice.id
                updated = replace(
                    invoice,
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
                continue

            # Nowa faktura

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
                timestamp=datetime.now()

            )
            print(invoice)
            self._invoice_repository.add(invoice)
            ref_map[invoice.invoice_number] = new_id

        return ref_map

    def _get_existing_invoice(self, invoice: InvoiceUpdate) -> Invoice | None:
        unque_invoice = self._invoice_repository.get_unique_invoice(invoice.invoice_number,invoice.seller_id)

        return unque_invoice if unque_invoice else None

    def mark_processed(self, invoice_ids: list[UUID]) -> None:
        for inv_id in invoice_ids:
            invoice = self._invoice_repository.get(inv_id)

            if invoice is None:
                raise ValueError(f"Invoice not found: {inv_id}")

            # idempotencja – jeśli już PROCESSED, nie ruszamy
            if invoice.status == InvoiceStatus.PROCESSED:
                continue

            updated = replace(
                invoice,
                status=InvoiceStatus.PROCESSED,
            )
            self._invoice_repository.update(updated)

