from abc import ABC, abstractmethod
from pathlib import Path

from contract_costs.model.invoice import Invoice
from contract_costs.model.invoice_line import InvoiceLine
from contract_costs.services.invoices.dto.export.assignment_export_bundle import InvoiceAssignmentExportBundle


class InvoiceAssignmentExporter(ABC):

    @abstractmethod
    def export(
        self,
        bundle: InvoiceAssignmentExportBundle
    ) -> None:
        """
        Export invoices and their lines
        into assignment format (e.g. Excel).
        """
        ...
