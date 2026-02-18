from dataclasses import dataclass

from contract_costs.action_bus.action_type import ActionType, action_type
from contract_costs.action_bus.query import Query


@dataclass(frozen=True, slots=True)
@action_type(ActionType.ORG_QUERY)
class ListUserOrganizationsQuery(Query):
    pass