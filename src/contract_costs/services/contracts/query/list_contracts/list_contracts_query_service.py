from collections.abc import Callable
from datetime import date
from uuid import UUID

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.model.value_direction import ValueDirection
from contract_costs.repository.value_type_repository import ValueTypeRepository
from contract_costs.services.contracts.financials.contract_financials import ContractFinancials
from contract_costs.services.contracts.financials.contract_financials_calculator import (
    ContractFinancialsCalculator,
)
from contract_costs.services.contracts.query.dto.contract_list_dto import ContractListDTO
from contract_costs.services.contracts.query.list_contracts.list_contracts_query_command import ListContractsQuery
from contract_costs.unit_of_work import UnitOfWork


class ListContractsQueryService(ActionHandler[ListContractsQuery, list[ContractListDTO]]):

    def __init__(self, *, today: Callable[[], date] = date.today) -> None:
        self._today = today

    def execute(
        self,
        *,
        action: ListContractsQuery,
        uow: UnitOfWork,
    ) -> list[ContractListDTO]:

        vt_direction = self._load_value_type_directions(
            organization_id=action.organization_id,
            value_type_repo=uow.value_types,
        )

        contracts = uow.contracts.list_contracts(
            organization_id=action.organization_id,
            contract_type=action.contract_type,
            status=action.status,
            search=action.search,
        )

        today = self._today()
        result: list[ContractListDTO] = []

        for contract in contracts:
            financials = ContractFinancialsCalculator.calculate(
                nodes=uow.contract_nodes.list_by_contract(
                    contract_id=contract.id,
                    organization_id=action.organization_id,
                ),
                lines=uow.financial_record_lines.list_by_contract(
                    contract_id=contract.id,
                    organization_id=action.organization_id,
                ),
                value_type_directions=vt_direction,
                start_date=contract.start_date,
                end_date=contract.end_date,
                today=today,
            )

            result.append(self._build_dto(contract=contract, financials=financials))

        return result

    @staticmethod
    def _load_value_type_directions(
        *,
        value_type_repo: ValueTypeRepository,
        organization_id: UUID,
    ) -> dict[UUID, ValueDirection]:
        value_types = value_type_repo.list_all(organization_id=organization_id)
        return {vt.id: vt.direction for vt in value_types}

    @staticmethod
    def _build_dto(
        *,
        contract,
        financials: ContractFinancials,
    ) -> ContractListDTO:
        total = financials.total
        return ContractListDTO(
            contract_id=contract.id,
            code=contract.code,
            name=contract.name,
            status=contract.status.value,
            is_active=contract.is_active,
            planned_budget=total.budget,
            progress=total.progress,
            net=total.cost.net,
            non_deduction=total.cost.non_tax,
            revenue=total.revenue.net,
            revenue_non_deductible=total.revenue.non_tax,
            financials=financials,
        )
