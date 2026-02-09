from abc import ABC, abstractmethod
from datetime import date
from uuid import UUID

from contract_costs.model.snapshot.contract_snapshot import ContractSnapshot


class ContractSnapshotRepository(ABC):

    # =========================
    # CREATE
    # =========================

    @abstractmethod
    def add(self, snapshot: ContractSnapshot) -> None:
        ...


    # =========================
    # READ
    # =========================

    @abstractmethod
    def get(
        self,
        *,
        organization_id: UUID,
        snapshot_id: UUID,
    ) -> ContractSnapshot | None:
        ...

    @abstractmethod
    def get_by_contract_and_date(
        self,
        *,
        organization_id: UUID,
        contract_id: UUID,
        snapshot_date: date,
    ) -> ContractSnapshot | None:
        ...

    @abstractmethod
    def list_by_contract(
        self,
        *,
        organization_id: UUID,
        contract_id: UUID,
    ) -> list[ContractSnapshot]:
        ...

    # =========================
    # TECHNICAL / ADMIN
    # =========================

    @abstractmethod
    def list_all(
        self,
        *,
        organization_id: UUID,
    ) -> list[ContractSnapshot]:
        ...
