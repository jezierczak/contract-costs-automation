from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.model.value_direction import ValueDirection
from contract_costs.services.value_types.query.value_type_mapper import ValueTypeMapper
from contract_costs.services.value_types.query.dto.value_type_dto import ValueTypeDTO
from contract_costs.services.value_types.query.dto.value_type_query import ValueTypeQuery
from contract_costs.unit_of_work import UnitOfWork


class ValueTypeQueryService(
        ActionHandler[ValueTypeQuery, list[ValueTypeDTO]]
    ):

    def execute(
        self,
        *,
        action: ValueTypeQuery,
        uow: UnitOfWork
    ) -> list[ValueTypeDTO]:
        repo = uow.value_types
        items = repo.list_all(organization_id=action.organization_id)

        if not action.include_inactive:
            items = [v for v in items if v.is_active]

        if action.direction:
            direction = ValueDirection(action.direction)
            items = [v for v in items if v.direction == direction]

        if action.code:
            items = [v for v in items if v.code == action.code]

        if action.search:
            q = action.search.lower()
            items = [
                v for v in items
                if q in v.name.lower()
                or (v.description and q in v.description.lower())
            ]

        return [ValueTypeMapper.to_dto(v) for v in items]
