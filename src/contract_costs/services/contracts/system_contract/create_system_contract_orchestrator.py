from uuid import UUID

from contract_costs.model.company import Company
from contract_costs.model.contract import ContractStatus, ContractType
from contract_costs.model.contract_node import ContractNodeInput
from contract_costs.repository.contract_repository import ContractRepository
from contract_costs.services.contracts.create_contract_service import CreateContractService
from contract_costs.services.contracts.dto.create_contract_command import CreateContractCommand


class CreateSystemContractOrchestrator:

    def __init__(
        self,
        contract_repository: ContractRepository,
        create_contract_service: CreateContractService,
    ) -> None:
        self._repo = contract_repository
        self._create = create_contract_service

    def execute(
        self,
        *,
        organization_id: UUID,
        actor_user_id: UUID,
        owner: Company,
    ) -> None:

        existing = self._repo.get_system_contract(
            organization_id=organization_id,
            owner_id=owner.id,
        )

        if existing:
            return  # idempotent

        command = CreateContractCommand(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            code=f"SYSTEM_{owner.tax_number}",
            name=f"Koszty działalności – {owner.name}",
            description="Koszty wspólne prowadzenia działalności",
            owner=owner,
            client=None,
            start_date=None,
            end_date=None,
            budget=None,
            path=None,
            status=ContractStatus.ACTIVE,
            contract_type=ContractType.SYSTEM,
            contract_node_input= self._default_system_tree()
        )

        self._create.execute(command=command)

    @staticmethod
    def _node( code: str, name: str) -> ContractNodeInput:
        return {
            "code": code,
            "name": name,
            "budget": None,
            "quantity": None,
            "unit": None,
            "children": [],
            "is_active": True,
        }

    def _default_system_tree(self) -> list[ContractNodeInput]:
        return [
            {
                "code": "ROOT",
                "name": "Koszty działalności",
                "budget": None,
                "quantity": None,
                "unit": None,
                "is_active": True,
                "children": [
                    self._node("ADMIN", "Administracja"),
                    self._node("FIN", "Kredyty/Pożyczki/Leasingi"),
                    self._node("UTIL", "Media"),
                    self._node("TAX", "Podatki"),
                    self._node("ZUS", "Ubezpieczenie ZUS"),
                    self._node("BOOK", "Księgowość"),
                    self._node("OTHER", "Pozostałe"),
                ],
            }
        ]
