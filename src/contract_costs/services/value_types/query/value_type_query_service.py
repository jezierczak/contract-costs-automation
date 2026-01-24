from contract_costs.model.value_direction import ValueDirection
from contract_costs.repository.value_type_repository import ValueTypeRepository
from contract_costs.services.value_types.query.value_type_mapper import ValueTypeMapper
from contract_costs.services.value_types.query.dto.value_type_dto import ValueTypeDTO
from contract_costs.services.value_types.query.dto.value_type_query import ValueTypeQuery


class ValueTypeQueryService:

    def __init__(self, repository: ValueTypeRepository) -> None:
        self._repository = repository

    def list(self, query: ValueTypeQuery) -> list[ValueTypeDTO]:
        items = self._repository.list()

        if not query.include_inactive:
            items = [v for v in items if v.is_active]

        if query.direction:
            direction = ValueDirection(query.direction)
            items = [v for v in items if v.direction == direction]

        if query.code:
            items = [v for v in items if v.code == query.code]

        if query.search:
            q = query.search.lower()
            items = [
                v for v in items
                if q in v.name.lower()
                or (v.description and q in v.description.lower())
            ]

        return [ValueTypeMapper.to_dto(v) for v in items]
