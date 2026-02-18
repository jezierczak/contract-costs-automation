from decimal import Decimal
from datetime import date
from pathlib import Path
from uuid import UUID

from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now
from contract_costs.model.contract import Contract, ContractStatus, ContractType
from tests.builders.company_builder import CompanyBuilder
from contract_costs.model.company import Company


class ContractBuilder:
    def __init__(self):
        now = utc_now()

        self._id = new_uuid()
        self._organization_id = new_uuid()
        self._created_at = now
        self._created_by_user_id = None
        self._updated_at = None
        self._updated_by_user_id = None

        self._code = "C-001"
        self._name = "Test Contract"
        self._owner = CompanyBuilder().build()
        self._client = None
        self._description = None
        self._start_date = None
        self._end_date = None
        self._budget = Decimal("1000.00")
        self._path = None
        self._status = ContractStatus.PLANNED
        self._contract_type = ContractType.PROJECT

    # ---------- build ----------

    def build(self) -> Contract:
        return Contract(
            id=self._id,
            organization_id=self._organization_id,
            created_at=self._created_at,
            created_by_user_id=self._created_by_user_id,
            updated_at=self._updated_at,
            updated_by_user_id=self._updated_by_user_id,
            code=self._code,
            name=self._name,
            owner=self._owner,
            client=self._client,
            description=self._description,
            start_date=self._start_date,
            end_date=self._end_date,
            budget=self._budget,
            path=self._path,
            status=self._status,
            contract_type=ContractType.PROJECT
        )

    # ---------- base ----------

    def with_id(self, id_: UUID) -> "ContractBuilder":
        self._id = id_
        return self

    def with_organization_id(self, org_id: UUID) -> "ContractBuilder":
        self._organization_id = org_id
        return self

    def with_code(self, code: str) -> "ContractBuilder":
        self._code = code
        return self

    def with_name(self, name: str) -> "ContractBuilder":
        self._name = name
        return self

    def with_description(self, description: str | None) -> "ContractBuilder":
        self._description = description
        return self

    def with_status(self, status: ContractStatus) -> "ContractBuilder":
        self._status = status
        return self

    # ---------- dates ----------

    def with_start_date(self, start_date: date | None) -> "ContractBuilder":
        self._start_date = start_date
        return self

    def with_end_date(self, end_date: date | None) -> "ContractBuilder":
        self._end_date = end_date
        return self

    # ---------- finance ----------

    def with_budget(self, budget: Decimal | None) -> "ContractBuilder":
        self._budget = budget
        return self

    # ---------- relations ----------

    def with_owner(self, owner: Company) -> "ContractBuilder":
        self._owner = owner
        return self

    def with_client(self, client: Company | None) -> "ContractBuilder":
        self._client = client
        return self

    # ---------- filesystem ----------

    def with_path(self, path: Path | None) -> "ContractBuilder":
        self._path = path
        return self

    def with_contract_type(self,contract_type: ContractType | None) -> "ContractBuilder":
        self._contract_type = contract_type if contract_type else ContractType.PROJECT
        return self
