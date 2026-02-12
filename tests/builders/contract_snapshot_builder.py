from datetime import date
from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now
from contract_costs.model.snapshot.contract_snapshot import (
    ContractSnapshot,
)


class ContractSnapshotBuilder:
    def __init__(self):
        now = utc_now()

        self._id = new_uuid()
        self._organization_id = new_uuid()
        self._created_at = now
        self._created_by_user_id = None
        # self._updated_at = None
        # self._updated_by_user_id = None

        self._contract_id = new_uuid()
        self._snapshot_date = date.today()

    def build(self) -> ContractSnapshot:
        return ContractSnapshot(
            id=self._id,
            organization_id=self._organization_id,
            created_at=self._created_at,
            created_by_user_id=self._created_by_user_id,
            # updated_at=self._updated_at,
            # updated_by_user_id=self._updated_by_user_id,
            contract_id=self._contract_id,
            snapshot_date=self._snapshot_date,
        )

    def with_organization_id(self, org_id):
        self._organization_id = org_id
        return self

    def with_contract_id(self, contract_id):
        self._contract_id = contract_id
        return self

    def with_snapshot_date(self, snapshot_date):
        self._snapshot_date = snapshot_date
        return self
