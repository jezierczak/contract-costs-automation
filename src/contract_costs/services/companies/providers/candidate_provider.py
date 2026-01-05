from abc import ABC, abstractmethod
from contract_costs.services.invoices.assigment.invoice_sources.pdf.parsers.dto.parse import CompanyInput
from contract_costs.model.company import Company


class CompanyCandidateProvider(ABC):
    """
    Odpowiada na pytanie:
    'Jakie firmy W OGÓLE warto rozważyć dla tych danych?'

    - grzebie w repo
    - zero decyzji
    - zero confidence
    """

    @abstractmethod
    def find_candidates(
        self,
        input_: CompanyInput
    ) -> list[Company]:
        """
        Zwraca 0..N potencjalnych kandydatów.
        """
        raise NotImplementedError
