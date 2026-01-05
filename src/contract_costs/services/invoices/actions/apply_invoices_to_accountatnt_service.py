# from dataclasses import replace
#
# from contract_costs.model.invoice import InvoiceStatus
# from contract_costs.repository.invoice_repository import InvoiceRepository
# from contract_costs.services.invoices.actions.dto.invoice_apply_row import InvoiceApplyRow
#
#
# class ApplyInvoicesToAccountantService:
#
#     def __init__(self, invoice_repo: InvoiceRepository):
#         self._invoice_repo = invoice_repo
#
#     def execute(self, rows: list[InvoiceApplyRow]) -> int:
#         updated = 0
#
#         for row in rows:
#             if not row.selected:
#                 continue
#
#             invoice = self._invoice_repo.get(row.invoice_id)
#             if not invoice:
#                 continue
#
#             # 🔒 zabezpieczenie
#             if invoice.status == InvoiceStatus.SENT_TO_ACCOUNTANT:
#                 continue
#
#             updated_invoice = replace(
#                 invoice,
#                 status=InvoiceStatus.SENT_TO_ACCOUNTANT,
#             )
#
#             self._invoice_repo.update(updated_invoice)
#             updated += 1
#
#         return updated
