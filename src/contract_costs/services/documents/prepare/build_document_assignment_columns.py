from uuid import UUID

from contract_costs.infrastructure.excel.excel_column_v2.dropdown_options import DropdownOptions
from contract_costs.infrastructure.excel.excel_column_v2.excel_column import ExcelColumn
from contract_costs.infrastructure.excel.excel_column_v2.excel_column_type import ExcelColumnType
from contract_costs.services.documents.prepare.dto.prepare_document_dto import PreparedDocumentDto

import contract_costs.config as cfg


def build_document_assignment_columns(

) -> list[ExcelColumn[PreparedDocumentDto]]:

    return ExcelColumn.from_lists(
        headers=[
            "ID",
            "Action",
            "Attach To Record",
            "Source",
            "Type",
            "Document Number",
            "Seller NIP",
            "File",
        ],
        names=[
            "document_id",
            "action",
            "target_record",
            "source",
            "type",
            "document_number",
            "seller_nip",
            "file_path",
        ],
        getters=[
            lambda d: str(d.document_id),

            # ACTION – domyślnie CREATE_NEW
            lambda d: "CREATE_NEW",

            # ATTACH – puste pole (uzupełnia user)
            lambda d: None,

            lambda d: d.document_source,
            lambda d: d.document_type,
            lambda d: d.document_number,
            lambda d: d.seller_nip,

            lambda d:  d.file_path,
        ],
        types=[
            ExcelColumnType.HIDDEN,
            ExcelColumnType.DROPDOWN,
            ExcelColumnType.DROPDOWN,
            ExcelColumnType.DISPLAY,
            ExcelColumnType.DROPDOWN,
            ExcelColumnType.DISPLAY,
            ExcelColumnType.DISPLAY,
            ExcelColumnType.LINK,
        ],
        editable=[
            False,
            True,
            True,
            False,
            True,
            True,
            True,
            False,
        ],
        dropdowns=[
            None,

            # ACTION
            DropdownOptions(dictionary="document_action"),

            # RECORD zależny od ID
            DropdownOptions(
                dictionary="existing_records",
                depends_on="seller_nip",
            ),

            None,

            # TYPE
            DropdownOptions(dictionary="document_type"),

            None,
            None,
            None,
        ],
    )
