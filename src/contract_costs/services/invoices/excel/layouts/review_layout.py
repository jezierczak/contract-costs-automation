from contract_costs.infrastructure.excel.excel_column import ExcelColumn, ExcelColumnType
from contract_costs.services.invoices.review.dto.invoice_review_item_view import InvoiceReviewItemView

REVIEW_COLUMNS: list[ExcelColumn[InvoiceReviewItemView]] = [
    ExcelColumn("INVOICE_ID", lambda x: str(x.invoice_id), ExcelColumnType.HIDDEN),
    ExcelColumn("Invoice No", lambda x: x.invoice_number),
    ExcelColumn("Invoice Date", lambda x: x.invoice_date),
    ExcelColumn("Buyer", lambda x: x.buyer_name),
    ExcelColumn("Seller", lambda x: x.seller_name),
    ExcelColumn("Seller Nip", lambda x: x.seller_tax_number),
    ExcelColumn("Method", lambda x: x.payment_method),
    ExcelColumn("Payment", lambda x: x.payment_status),
    ExcelColumn("Net", lambda x: x.total_net),
    ExcelColumn("Vat", lambda x: x.total_vat),
    ExcelColumn("Gross", lambda x: x.total_gross),
    ExcelColumn("Not Evidenced", lambda x: x.total_not_evidenced),
    ExcelColumn("Status", lambda x: x.status),
    ExcelColumn("Link", lambda x: x.scan_filename, ExcelColumnType.LINK),
    ExcelColumn("Folder", lambda x: x.scan_filename, ExcelColumnType.FOLDER),
]
