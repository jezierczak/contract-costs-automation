from contract_costs.model.value_type import ValueType
from contract_costs.services.value_types.query.dto.value_type_dto import ValueTypeDTO


class ValueTypeMapper:
    @staticmethod
    def to_dto(vt: ValueType) -> ValueTypeDTO:
        return ValueTypeDTO(
            id=vt.id,
            code=vt.code,
            name=vt.name,
            description=vt.description,
            direction=vt.direction.value,
            is_active=vt.is_active,
        )
