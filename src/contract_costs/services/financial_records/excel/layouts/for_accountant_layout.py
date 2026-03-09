from contract_costs.infrastructure.excel.excel_column import ExcelColumn, ExcelColumnType
from contract_costs.services.financial_records.review.dto.invoice_review_item_view import FinancialRecordReviewItemView

ACCOUNTANT_COLUMNS: list[ExcelColumn[FinancialRecordReviewItemView]] = [
    # ExcelColumn("X", lambda _: False, ExcelColumnType.CHECKBOX, editable=True),
    ExcelColumn("ACTION", lambda _: "none", ExcelColumnType.DROPDOWN, editable=True,
                options=["none", "approved", "reopen"], ),
    ExcelColumn("INVOICE_ID", lambda x: str(x.record_id), ExcelColumnType.HIDDEN),

    ExcelColumn("Invoice No", lambda x: x.reference),
    ExcelColumn("Invoice Date", lambda x: x.invoice_date),
    ExcelColumn("Buyer", lambda x: x.buyer_name),
    ExcelColumn("Buyer NIP", lambda x: x.buyer_tax_number),
    ExcelColumn("Seller", lambda x: x.seller_name),
    ExcelColumn("Seller NIP", lambda x: x.seller_tax_number),
    ExcelColumn("Net", lambda x: x.total_net),
    ExcelColumn("Vat", lambda x: x.total_vat),
    ExcelColumn("Gross", lambda x: x.total_gross),
    ExcelColumn("Not Evidenced", lambda x: x.total_not_evidenced),
    ExcelColumn("Link", lambda x: x.primary_document_path, ExcelColumnType.LINK),
    ExcelColumn("Folder", lambda x: x.primary_document_path, ExcelColumnType.FOLDER),

]
