from abc import ABC, abstractmethod
from pathlib import Path
from uuid import UUID

from contract_costs.services.financial_records.assigment.prepare.dto.assignment_export_bundle import FinancialRecordAssignmentExportBundle


class InvoiceAssignmentExporter(ABC):

    @abstractmethod
    def export(
        self,
        *,
        organization_id: UUID,
        bundle: FinancialRecordAssignmentExportBundle,
        output_path: Path
    ) -> None:
        """
        Export invoices and their lines
        into assignment format (e.g. Excel).
        """
        ...
