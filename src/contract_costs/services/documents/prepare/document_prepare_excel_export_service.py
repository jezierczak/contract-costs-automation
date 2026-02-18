from pathlib import Path

from contract_costs.infrastructure.excel.excel_column_v2.base_excel_exporter_v2 import BaseExcelExporterV2
from contract_costs.model.document import DocumentType
from contract_costs.services.documents.apply.dto.apply_document_command import DocumentApplyAction
from contract_costs.services.documents.prepare.build_document_assignment_columns import build_document_assignment_columns
# from contract_costs.services.documents.prepare.dto.document_prepare_excel_export_command import \
#     DocumentPrepareExcelExportCommand
from contract_costs.services.documents.prepare.dto.prepare_document_bundle import PrepareDocumentsBundle

from contract_costs.services.documents.prepare.dto.prepare_document_dto import (
    PreparedDocumentDto,
)


class DocumentPrepareExcelExportService:

    @staticmethod
    def export(
            *,
            organization_id: str,
            bundle: PrepareDocumentsBundle,
            output_path: Path
          ):

        _exporter = BaseExcelExporterV2[PreparedDocumentDto]()

        _exporter.register_dictionary(
            name="document_action",
            rows=[
                {"KEY": "ALL", "VALUE": doc_action.value}
                for doc_action in DocumentApplyAction
            ],
            hidden=True,
        )

        _exporter.register_dictionary(
            name="document_type",
            rows=[
                {"KEY": "ALL", "VALUE": t.value}
                for t in DocumentType
                if t != DocumentType.UNKNOWN
            ],
            hidden=True,
        )


        rows = []

        for doc in bundle.documents:
            for candidate in doc.candidates:
                label = f"{candidate.reference or 'NO_REF'} | {candidate.status} | {candidate.invoice_date or 'NO_DATE'}"

                rows.append(
                    {
                        "KEY": doc.seller_nip or "",
                        "VALUE": label,
                        "RECORD_ID": str(candidate.record_id)
                    }
                )

        if rows:
            _exporter.register_dictionary(
                name="existing_records",
                rows=rows,
                hidden=True,
            )
        else:
            # rejestrujemy pusty słownik z technicznym placeholderem
            _exporter.register_dictionary(
                name="existing_records",
                rows=[{"KEY": "NONE", "VALUE": "", "RECORD_ID":""}],
                hidden=True,
            )

        _exporter.add_sheet(
            organization_id=organization_id,
            items=bundle.documents,
            columns=build_document_assignment_columns(),
            sheet_name="Documents",
            header={
                "Organization": [str(organization_id)],
                "Total documents": [str(len(bundle.documents))],
            },
        )

        # =============================================
        # 4️⃣ SAVE
        # =============================================

        _exporter.save(output_path)
