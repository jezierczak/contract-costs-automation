from dataclasses import dataclass
from contract_costs.action_bus.action import Action


@dataclass(frozen=True)
class ListDocumentsQueryCommand(Action):
    has_payload: bool | None = None
    has_record: bool | None = None
    source: str | None = None