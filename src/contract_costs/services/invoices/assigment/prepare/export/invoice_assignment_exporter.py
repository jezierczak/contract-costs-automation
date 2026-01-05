from abc import ABC, abstractmethod
from pathlib import Path

from contract_costs.services.invoices.assigment.prepare.dto.assignment_export_bundle import InvoiceAssignmentExportBundle


class InvoiceAssignmentExporter(ABC):

    @abstractmethod
    def export(
        self,
        bundle: InvoiceAssignmentExportBundle,
        output_path: Path
    ) -> None:
        """
        Export invoices and their lines
        into assignment format (e.g. Excel).
        """
        ...
