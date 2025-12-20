from dataclasses import replace
from datetime import datetime
from uuid import uuid4, UUID

from contract_costs.model.invoice import Invoice, InvoiceStatus
from contract_costs.repository.invoice_repository import InvoiceRepository
from contract_costs.services.invoices.dto.common import InvoiceUpdate


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
            ref = update.ref

            # Istniejąca faktura
            if ref.invoice_id is not None:
                invoice = self._invoice_repository.get(ref.invoice_id)
                if invoice is None:
                    raise ValueError("Invoice not found")

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

            # Nowa faktura (external_ref)
            if ref.external_ref is None:
                raise ValueError("InvoiceRef must have invoice_id or external_ref")

            if ref.external_ref in ref_map:
                raise ValueError(f"Duplicate external_ref: {ref.external_ref}")

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

            self._invoice_repository.add(invoice)
            ref_map[ref.external_ref] = new_id

        return ref_map

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
