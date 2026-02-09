from pathlib import Path

from contract_costs.infrastructure.excel.excel_column_v2.base_excel_exporter_v2 import BaseExcelExporterV2
from contract_costs.model.document import DocumentType
from contract_costs.services.documents.apply.dto.apply_document_command import DocumentApplyAction
from contract_costs.services.documents.prepare.build_document_assignment_columns import build_document_assignment_columns

from contract_costs.services.documents.prepare.dto.prepare_document_dto import (
    PreparedDocumentDto,
)
from contract_costs.services.documents.prepare.dto.prepare_document_bundle import (
    PrepareDocumentsBundle
)


class DocumentPrepareExcelExportService:

    def __init__(self) -> None:
        self._exporter = BaseExcelExporterV2[PreparedDocumentDto]()

    def execute(
        self,
        *,
        organization_id,
        bundle: PrepareDocumentsBundle,
        output_path: Path,
    ) -> None:

        # =============================================
        # 1️⃣ REGISTER DICTIONARIES
        # =============================================

        # self._exporter.register_dictionary(
        #     name="document_source",
        #     rows=[
        #         {"KEY": "ALL", "VALUE": "PDF"},
        #         {"KEY": "ALL", "VALUE": "KSEF"},
        #         {"KEY": "ALL", "VALUE": "IMAGE"},
        #     ],
        #     hidden=True,
        # )

        self._exporter.register_dictionary(
            name="document_action",
            rows=[
                {"KEY": "ALL", "VALUE": action.value}
                for action in DocumentApplyAction
            ],
            hidden=True,
        )

        self._exporter.register_dictionary(
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
            self._exporter.register_dictionary(
                name="existing_records",
                rows=rows,
                hidden=True,
            )
        else:
            # rejestrujemy pusty słownik z technicznym placeholderem
            self._exporter.register_dictionary(
                name="existing_records",
                rows=[{"KEY": "NONE", "VALUE": "", "RECORD_ID":""}],
                hidden=True,
            )

        self._exporter.add_sheet(
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

        self._exporter.save(output_path)
