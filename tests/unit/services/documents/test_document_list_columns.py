from datetime import datetime
from uuid import uuid4

from contract_costs.services.documents.query.document_list_item_dto import DocumentListItemDto
from contract_costs.services.documents.query.printer_columns.document_list_columns import (
    document_list_columns,
)
from contract_costs.services.documents.query.printer_columns.document_list_columns_excel import (
    document_list_columns_excel,
)


def _sample_item() -> DocumentListItemDto:
    return DocumentListItemDto(
        document_id=uuid4(),
        file_name="invoice.pdf",
        document_source="pdf",
        document_type="invoice",
        document_number="FV/1",
        seller_nip="1234567890",
        has_payload=True,
        has_record=False,
        created_at=datetime(2026, 2, 17, 10, 0, 0),
        file_path="incoming/documents/invoice.pdf",
    )


def test_document_list_columns_maps_fields() -> None:
    item = _sample_item()
    columns = document_list_columns()

    assert len(columns) == 9
    assert columns[0].getter(item) == str(item.document_id)[:8]
    assert columns[6].getter(item) == "YES"
    assert columns[7].getter(item) == "NO"


def test_document_list_columns_excel_includes_link_and_folder_columns() -> None:
    item = _sample_item()
    columns = document_list_columns_excel()

    assert len(columns) == 11
    assert columns[9].getter(item) == item.file_path
    assert columns[10].getter(item) == item.file_path

