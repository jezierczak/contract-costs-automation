from abc import ABC, abstractmethod
from pathlib import Path

from contract_costs.services.invoices.dto.parse import InvoiceParseResult


class InvoiceParser(ABC):

    @abstractmethod
    def parse(self, file_path: Path) -> InvoiceParseResult:
        """
        Parse invoice file and return:
        - Invoice (status = NEW)
        - InvoiceLines without cost assignments
        """
        ...
