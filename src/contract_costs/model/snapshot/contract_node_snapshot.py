from dataclasses import dataclass
from uuid import UUID
from decimal import Decimal


@dataclass(frozen=True)
class ContractNodeSnapshot:
    id: UUID
    snapshot_id: UUID
    contract_node_id: UUID

    planned_budget: Decimal      # budżet planowany (z leafów)
    progress: Decimal            # 0.0–1.0 (dla leafów, agregowany wyżej)
