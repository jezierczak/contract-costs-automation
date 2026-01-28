from contract_costs.infrastructure.excel.excel_column_v2.excel_column import ExcelColumn
from contract_costs.infrastructure.excel.excel_column_v2.excel_column_type import ExcelColumnType
from contract_costs.services.invoices.review.dto.invoice_review_item_view import InvoiceReviewItemView


def invoice_list_columns() -> list[ExcelColumn[InvoiceReviewItemView]]:
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
            lambda i: i.invoice_number,
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