from decimal import Decimal
from uuid import UUID
from contract_costs.common.ids import new_uuid
from contract_costs.model.snapshot.contract_node_value_snapshot import (
    ContractNodeValueSnapshot,
)


class ContractNodeValueSnapshotBuilder:
    def __init__(self):
        self._id = new_uuid()
        self._node_snapshot_id = new_uuid()
        self._value_type_id = new_uuid()

        self._net = Decimal("100.00")
        self._vat = Decimal("23.00")
        self._gross = Decimal("123.00")
        self._non_deductible = Decimal("0.00")

    def build(self) -> ContractNodeValueSnapshot:
        return ContractNodeValueSnapshot(
            id=self._id,
            node_snapshot_id=self._node_snapshot_id,
            value_type_id=self._value_type_id,
            net=self._net,
            vat=self._vat,
            gross=self._gross,
            non_deductible=self._non_deductible,
        )

    def with_node_snapshot_id(self, node_snapshot_id: UUID):
        self._node_snapshot_id = node_snapshot_id
        return self
