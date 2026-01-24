from abc import ABC, abstractmethod
from datetime import date
from uuid import UUID

from contract_costs.model.snapshot.contract_snapshot import ContractSnapshot


class ContractSnapshotRepository(ABC):

    @abstractmethod
    def add(self, snapshot: ContractSnapshot) -> None:
        ...

    @abstractmethod
    def get(self, snapshot_id: UUID) -> ContractSnapshot | None:
        ...

    # @abstractmethod
    # def find_by_id_prefix(self, prefix: str) -> list[ContractSnapshot]:
    #     ...

    @abstractmethod
    def get_by_contract_and_date(
        self,
        *,
        contract_id: UUID,
        snapshot_date: date,
    ) -> ContractSnapshot | None:
        ...

    @abstractmethod
    def list_by_contract(
        self,
        contract_id: UUID,
    ) -> list[ContractSnapshot]:
        ...

    # techniczne
    @abstractmethod
    def list_all(self) -> list[ContractSnapshot]: ...
