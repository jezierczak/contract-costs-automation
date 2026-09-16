from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from typing import Callable

from contract_costs.repository.business_event_repository import BusinessEventRepository
from contract_costs.repository.company_dashboard.company_dashboard_repository import CompanyDashboardRepository
from contract_costs.repository.company_ksef_settings_repository import CompanyKsefSettingsRepository
from contract_costs.repository.company_repository import CompanyRepository
from contract_costs.repository.contract_node_repository import ContractNodeRepository
from contract_costs.repository.contract_repository import ContractRepository
from contract_costs.repository.document_repository import DocumentRepository
from contract_costs.repository.financial_record_line_repository import FinancialRecordLineRepository
from contract_costs.repository.financial_record_payment_repository import FinancialRecordPaymentRepository
from contract_costs.repository.financial_record_repository import FinancialRecordRepository
from contract_costs.repository.identity.organization_repository import OrganizationRepository
from contract_costs.repository.identity.organization_user_repository import OrganizationUserRepository
from contract_costs.repository.identity.user_repository import UserRepository
from contract_costs.repository.number_sequence_repository import NumberSequenceRepository
from contract_costs.repository.session_repository import SessionRepository
from contract_costs.repository.snapshot.contract_node_snapshot_repository import ContractNodeSnapshotRepository
from contract_costs.repository.snapshot.contract_node_value_snapshot_repository import (
    ContractNodeValueSnapshotRepository,
)
from contract_costs.repository.snapshot.contract_snapshot_repository import ContractSnapshotRepository
from contract_costs.repository.value_type_repository import ValueTypeRepository


logger = logging.getLogger(__name__)

class UnitOfWork(ABC):
    def __init__(self) -> None:
        ...
        self._post_commit_hooks: list[Callable[[], None]] = []
    @property
    @abstractmethod
    def companies(self) -> CompanyRepository:
        ...

    @property
    @abstractmethod
    def financial_records(self) -> FinancialRecordRepository:
        ...

    @property
    @abstractmethod
    def financial_record_lines(self) -> FinancialRecordLineRepository:
        ...

    @property
    @abstractmethod
    def financial_record_payments(self) -> FinancialRecordPaymentRepository:
        ...

    @property
    @abstractmethod
    def contracts(self) -> ContractRepository:
        ...

    @property
    @abstractmethod
    def contract_nodes(self) -> ContractNodeRepository:
        ...

    @property
    @abstractmethod
    def value_types(self) -> ValueTypeRepository:
        ...

    @property
    @abstractmethod
    def contract_snapshots(self) -> ContractSnapshotRepository:
        ...

    @property
    @abstractmethod
    def contract_node_snapshots(self) -> ContractNodeSnapshotRepository:
        ...

    @property
    @abstractmethod
    def contract_node_value_snapshots(self) -> ContractNodeValueSnapshotRepository:
        ...

    @property
    @abstractmethod
    def organizations(self) -> OrganizationRepository:
        ...

    @property
    @abstractmethod
    def organization_users(self) -> OrganizationUserRepository:
        ...

    @property
    @abstractmethod
    def users(self) -> UserRepository:
        ...

    @property
    @abstractmethod
    def documents(self) -> DocumentRepository:
        ...

    @property
    @abstractmethod
    def sessions(self) -> SessionRepository:
        ...

    @property
    @abstractmethod
    def number_sequences(self) -> NumberSequenceRepository:
        ...

    @property
    @abstractmethod
    def business_events(self) -> BusinessEventRepository:
        ...

    @property
    @abstractmethod
    def company_dashboard(self) -> CompanyDashboardRepository:
        ...

    @property
    @abstractmethod
    def company_ksef_settings(self) -> CompanyKsefSettingsRepository:
        ...

    @abstractmethod
    def commit(self) -> None:
        ...

    @abstractmethod
    def rollback(self) -> None:
        ...

    @abstractmethod
    def close(self) -> None:
        ...

    def add_post_commit_hook(self, hook: Callable[[], None]) -> None:
        self._post_commit_hooks.append(hook)

    def __enter__(self) -> UnitOfWork:
        self._started_at = time.perf_counter()
        logger.debug("UoW enter")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        try:
            if exc_type:
                logger.warning("UoW rollback due to exception: %s", exc_type)
                self.rollback()
                return

            self.commit()

            for hook in self._post_commit_hooks:
                try:
                    hook()
                except Exception:
                    logger.exception("Post-commit hook failed")
                    # NIE RAISE

        finally:
            self._post_commit_hooks.clear()
            self.close()

            duration = time.perf_counter() - self._started_at
            logger.debug("UoW finished in %.4fs", duration)
