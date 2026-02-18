from abc import ABC, abstractmethod
from uuid import UUID

from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.dto.parse import CompanyInput
from contract_costs.model.company import Company
from contract_costs.unit_of_work import UnitOfWork


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
        *,
        uow:UnitOfWork,
        organization_id: UUID,
        input_: CompanyInput,
    ) -> list[Company]:
        """
        Zwraca 0..N potencjalnych kandydatów.
        """
        raise NotImplementedError
