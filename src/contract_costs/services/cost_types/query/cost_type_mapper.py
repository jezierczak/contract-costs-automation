from contract_costs.model.cost_type import CostType
from contract_costs.services.cost_types.query.dto.cost_type_dto import CostTypeDTO


class CostTypeMapper:
    @staticmethod
    def to_dto(ct: CostType) -> CostTypeDTO:
        return CostTypeDTO(
            id=ct.id,
            code=ct.code,
            name=ct.name,
            description=ct.description,
            is_active=ct.is_active,
        )
