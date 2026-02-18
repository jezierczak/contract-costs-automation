from dataclasses import dataclass
from uuid import UUID

from contract_costs.action_bus.action_type import ActionType, action_type
from contract_costs.action_bus.query import Query


@dataclass(frozen=True, slots=True)
@action_type(ActionType.VIEW_SNAPSHOT)
class BaseContractSnapshotQuery(Query):
    pass

@dataclass(frozen=True, slots=True)
class ListContractSnapshotsQuery(BaseContractSnapshotQuery):
    contract_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class GetContractSnapshotQuery(BaseContractSnapshotQuery):
    snapshot_id_prefix: str