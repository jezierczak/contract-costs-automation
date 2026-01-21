from contract_costs.infrastructure.excel.excel_column import ExcelColumn, ExcelColumnType
from contract_costs.services.invoices.review.dto.invoice_for_accountant_view import InvoiceForAccountantView

ACCOUNTANT_COLUMNS: list[ExcelColumn[InvoiceForAccountantView]] = [
    # ExcelColumn("X", lambda _: False, ExcelColumnType.CHECKBOX, editable=True),
    ExcelColumn("ACTION",lambda _: "none",ExcelColumnType.DROPDOWN,editable=True,
                    options=["none", "approved", "reopen"],),
    ExcelColumn("INVOICE_ID", lambda x: str(x.invoice_id), ExcelColumnType.HIDDEN),

    ExcelColumn("Invoice No", lambda x: x.invoice_number),
    ExcelColumn("Invoice Date", lambda x: x.invoice_date),
    ExcelColumn("Buyer", lambda x: x.buyer_name),
    ExcelColumn("Buyer NIP", lambda x: x.buyer_tax_number),
    ExcelColumn("Seller", lambda x: x.seller_name),
    ExcelColumn("Seller NIP", lambda x: x.seller_tax_number),
    ExcelColumn("Net", lambda x: x.total_net),
    ExcelColumn("Vat", lambda x: x.total_vat),
    ExcelColumn("Gross", lambda x: x.total_gross),
    ExcelColumn("Not Evidenced", lambda x: x.total_not_evidenced),
    ExcelColumn("Link", lambda x: x.scan_filename, ExcelColumnType.LINK),
    ExcelColumn("Folder", lambda x: x.scan_filename, ExcelColumnType.FOLDER),

]
