from contract_costs.model.contract import Contract
from contract_costs.services.contracts.prepare.dto.contract_prepare_dto import (
    ContractPrepareDTO,
)


class ContractPrepareMapper:
    """
    Maps domain Contract → ContractPrepareDTO
    Used ONLY for prepare (Excel export).
    """

    @staticmethod
    def map(contract: Contract) -> ContractPrepareDTO:
        return ContractPrepareDTO(
            code=contract.code,
            name=contract.name,
            owner_nip=contract.owner.tax_number,
            client_nip=contract.client.tax_number if contract.client else None,
            description=contract.description,
            start_date=contract.start_date,
            end_date=contract.end_date,
            budget=contract.budget,
            path=str(contract.path),
            status=contract.status.name,
        )
