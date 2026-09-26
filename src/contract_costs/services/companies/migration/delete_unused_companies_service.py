import logging
from uuid import UUID

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.model.company import Company, CompanyType
from contract_costs.services.companies.migration.delete_unused_companies_command import (
    DeleteUnusedCompaniesCommand,
)
from contract_costs.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)


class DeleteUnusedCompaniesService(
    ActionHandler[DeleteUnusedCompaniesCommand, list[Company]]
):
    """
    Sprzątanie firm bez żadnych powiązań (np. placeholdery z OCR, firmy
    osierocone po `repair-record-companies`).

    Firma jest nieużywana, gdy nie jest OWN i nie odwołuje się do niej:
    - żaden rekord finansowy (również usunięty – FK w bazie),
    - żaden kontrakt (właściciel lub klient),
    - ustawienia KSeF.
    Bez `apply` tylko zwraca listę; z `apply` usuwa firmy.
    """

    def execute(
        self,
        *,
        action: DeleteUnusedCompaniesCommand,
        uow: UnitOfWork,
    ) -> list[Company]:
        org_id = action.organization_id
        used: set[UUID] = set()

        for record in uow.financial_records.list_all(organization_id=org_id):
            used.update({record.seller_id, record.buyer_id})

        for contract in uow.contracts.list_contracts(organization_id=org_id):
            used.add(contract.owner.id)
            if contract.client:
                used.add(contract.client.id)

        unused = [
            company
            for company in uow.companies.list_all(org_id)
            if company.role != CompanyType.OWN
            and company.id not in used
            and uow.company_ksef_settings.get_by_company_id(
                organization_id=org_id, company_id=company.id,
            ) is None
        ]

        if action.apply:
            for company in unused:
                logger.info("Deleting unused company %s (%s)", company.name, company.tax_number)
                uow.companies.delete(company.id, org_id)

        return unused
