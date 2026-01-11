from contract_costs.repository.cost_type_repository import CostTypeRepository
from contract_costs.services.cost_types.query.cost_type_mapper import CostTypeMapper
from contract_costs.services.cost_types.query.dto.cost_type_dto import CostTypeDTO
from contract_costs.services.cost_types.query.dto.cost_type_query import CostTypeQuery


class CostTypeQueryService:

    def __init__(self, repository: CostTypeRepository) -> None:
        self._repository = repository

    def list(self, query: CostTypeQuery) -> list[CostTypeDTO]:
        items = self._repository.list()

        if not query.include_inactive:
            items = [c for c in items if c.is_active]

        if query.code:
            items = [c for c in items if c.code == query.code]

        if query.search:
            q = query.search.lower()
            items = [
                c for c in items
                if q in c.name.lower()
                or (c.description and q in c.description.lower())
            ]

        return [CostTypeMapper.to_dto(c) for c in items]
