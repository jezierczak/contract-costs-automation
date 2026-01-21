from contract_costs.infrastructure.excel.excel_column import ExcelColumn, ExcelColumnType
from contract_costs.services.invoices.review.dto.unpaid_invoice_view import UnpaidInvoiceView

UNPAID_COLUMNS: list[ExcelColumn[UnpaidInvoiceView]] = [
    ExcelColumn("PAID", lambda x: x.payment_status == "PAID",
                ExcelColumnType.CHECKBOX, editable=True),
    ExcelColumn("INVOICE_ID", lambda x: str(x.invoice_id),
                ExcelColumnType.HIDDEN),

    ExcelColumn("Invoice No", lambda x: x.invoice_number),
    ExcelColumn("Buyer", lambda x: x.buyer_name),
    ExcelColumn("Seller", lambda x: x.seller_name),
    ExcelColumn("Seller Nip", lambda x: x.seller_tax_number),
    ExcelColumn("Bank Account", lambda x: x.seller_bank_account),
    ExcelColumn("Payment Method", lambda x: x.payment_method),
    ExcelColumn("Due Date", lambda x: x.due_date),
    ExcelColumn("Net", lambda x: x.total_net),
    ExcelColumn("Vat", lambda x: x.total_vat),
    ExcelColumn("Gross", lambda x: x.total_gross),
    ExcelColumn("Link", lambda x: x.scan_filename, ExcelColumnType.LINK),
    ExcelColumn("Folder", lambda x: x.scan_filename, ExcelColumnType.FOLDER),
]
