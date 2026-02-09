from contract_costs.infrastructure.excel.excel_column_v2.excel_column import ExcelColumn
from contract_costs.infrastructure.excel.excel_column_v2.excel_column_type import ExcelColumnType
from contract_costs.services.financial_records.review.dto.invoice_review_item_view import FinancialRecordReviewItemView

def financial_record_list_columns() -> list[ExcelColumn[FinancialRecordReviewItemView]]:
    return ExcelColumn.from_lists(
        headers=[
            "NUMER FAKTURY",
            "DATA FAKT.",
            "NABYWCA",
            "SPRZEDAWCA",
            "NETTO",
            "VAT",
            "BRUTTO",
            "NIEOPOD.",
            "METODA PŁ.",
            "STATUS PŁ.",
            "ZAPŁ. DO",
            "STATUS",
            "DIRECTION",
            "CONTRACTS",

        ],
        getters=[
            lambda i: i.reference,
            lambda i: i.invoice_date,
            lambda i: i.buyer_tax_number,
            lambda i: i.seller_tax_number,
            lambda i: i.total_net,
            lambda i: i.total_vat,
            lambda i: i.total_gross,
            lambda i: i.total_not_evidenced,
            lambda i: i.payment_method,
            lambda i: i.payment_status,
            lambda i: i.due_date,
            lambda i: i.status,
            lambda i: i.direction,
            lambda i: i.contract_codes,

        ],
        types=[
            ExcelColumnType.DISPLAY,   # invoice number
            ExcelColumnType.DISPLAY,   # date
            ExcelColumnType.DISPLAY,   # buyer
            ExcelColumnType.DISPLAY,   # seller
            ExcelColumnType.DISPLAY,   # net
            ExcelColumnType.DISPLAY,   # vat
            ExcelColumnType.DISPLAY,   # gross
            ExcelColumnType.DISPLAY,   # not evidenced
            ExcelColumnType.DISPLAY,   # payment method
            ExcelColumnType.DISPLAY,   # payment status
            ExcelColumnType.DISPLAY,   # due date
            ExcelColumnType.DISPLAY,   # status
            ExcelColumnType.DISPLAY,   # direction
            ExcelColumnType.DISPLAY,   # contracts

        ],
        agg=[
            False,  # invoice number
            False,  # date
            False,  # buyer
            False,  # seller
            True,   # NET
            True,   # VAT
            True,   # GROSS
            True,   # NOT EVIDENCED
            False,  # payment method
            False,  # payment status
            False,  # due date
            False,  # status
            False,  # direction
            False,  # contracts

        ],
    )

def financial_record_list_columns_excel() -> list[ExcelColumn[FinancialRecordReviewItemView]]:
    return ExcelColumn.from_lists(
        headers=[
            "NUMER FAKTURY",
            "DATA FAKT.",
            "NABYWCA",
            "SPRZEDAWCA",
            "NETTO",
            "VAT",
            "BRUTTO",
            "NIEOPOD.",
            "METODA PŁ.",
            "STATUS PŁ.",
            "ZAPŁ. DO",
            "STATUS",
            "DIRECTION",
            "CONTRACTS",
            "LINK",
            "FOLDER",
        ],
        getters=[
            lambda i: i.reference,
            lambda i: i.invoice_date,
            lambda i: i.buyer_tax_number,
            lambda i: i.seller_tax_number,
            lambda i: i.total_net,
            lambda i: i.total_vat,
            lambda i: i.total_gross,
            lambda i: i.total_not_evidenced,
            lambda i: i.payment_method,
            lambda i: i.payment_status,
            lambda i: i.due_date,
            lambda i: i.status,
            lambda i: i.direction,
            lambda i: i.contract_codes,
            lambda i: i.primary_document_path,
            lambda i: i.primary_document_path,
        ],
        types=[
            ExcelColumnType.DISPLAY,   # invoice number
            ExcelColumnType.DATE,   # date
            ExcelColumnType.DISPLAY,   # buyer
            ExcelColumnType.DISPLAY,   # seller
            ExcelColumnType.NUMBER,   # net
            ExcelColumnType.NUMBER,   # vat
            ExcelColumnType.NUMBER,   # gross
            ExcelColumnType.NUMBER,   # not evidenced
            ExcelColumnType.DISPLAY,   # payment method
            ExcelColumnType.DISPLAY,   # payment status
            ExcelColumnType.DATE,   # due date
            ExcelColumnType.DISPLAY,   # status
            ExcelColumnType.DISPLAY,   # direction
            ExcelColumnType.DISPLAY,   # contracts
            ExcelColumnType.LINK,
            ExcelColumnType.FOLDER,
        ],
        agg=[
            False,  # invoice number
            False,  # date
            False,  # buyer
            False,  # seller
            True,   # NET
            True,   # VAT
            True,   # GROSS
            True,   # NOT EVIDENCED
            False,  # payment method
            False,  # payment status
            False,  # due date
            False,  # status
            False,  # direction
            False,  # contracts
            False,
            False
        ],
    )