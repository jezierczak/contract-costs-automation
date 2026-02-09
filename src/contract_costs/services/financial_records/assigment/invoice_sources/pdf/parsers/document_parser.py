from abc import ABC, abstractmethod
from pathlib import Path

from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.dto.parse import DocumentParseResult


class DocumentParser(ABC):

    @abstractmethod
    def parse(self, file_path: Path) -> DocumentParseResult:
        """
        Parse invoice file and return:
        - Invoice (status = NEW)
        - InvoiceLines without cost assignments
        """
        ...
