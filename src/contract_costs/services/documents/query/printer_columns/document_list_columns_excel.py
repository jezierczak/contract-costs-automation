from contract_costs.infrastructure.excel.excel_column_type import ExcelColumnType
from contract_costs.infrastructure.excel.excel_column_v2.excel_column import ExcelColumn
from contract_costs.services.documents.query.document_list_item_dto import DocumentListItemDto


def document_list_columns_excel() -> list[ExcelColumn[DocumentListItemDto]]:
    return ExcelColumn.from_lists(
        headers=[
            "ID",
            "PLIK",
            "ŹRÓDŁO",
            "TYP",
            "NUMER",
            "SPRZEDAWCA NIP",
            "SPARSOWANY",
            "PRZYPISANY",
            "UTWORZONO",
            "LINK",
            "FOLDER",
        ],
        getters=[
            lambda d: str(d.document_id)[:8],
            lambda d: d.file_name,
            lambda d: d.document_source,
            lambda d: d.document_type,
            lambda d: d.document_number or "-",
            lambda d: d.seller_nip or "-",
            lambda d: "YES" if d.has_payload else "NO",
            lambda d: "YES" if d.has_record else "NO",
            lambda d: d.created_at,
            lambda d: d.file_path,  # klikany link do pliku
            lambda d: d.file_path,  # folder
        ],
        types=[
            ExcelColumnType.DISPLAY,
            ExcelColumnType.DISPLAY,
            ExcelColumnType.DISPLAY,
            ExcelColumnType.DISPLAY,
            ExcelColumnType.DISPLAY,
            ExcelColumnType.DISPLAY,
            ExcelColumnType.DISPLAY,
            ExcelColumnType.DISPLAY,
            ExcelColumnType.DATE,
            ExcelColumnType.LINK,
            ExcelColumnType.FOLDER,
        ],
        agg=[
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
        ],
    )
