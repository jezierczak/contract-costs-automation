from abc import ABC, abstractmethod
from typing import Protocol
from uuid import UUID

from contract_costs.model.number_sequence import NumberSequence


class NumberSequenceRepository(ABC):
    @abstractmethod
    def get(
        self,
        organization_id: UUID,
        scope_key: str,
    ) -> NumberSequence | None:
        """
        Odczytuje sekwencję bez blokowania.
        """
        ...

    @abstractmethod
    def get_for_update(
        self,
        organization_id: UUID,
        scope_key: str,
    ) -> NumberSequence | None:
        """
        Pobiera sekwencję dla (organization_id, scope_key)
        i blokuje ją do końca transakcji.
        """
        ...

    @abstractmethod
    def add(
        self,
        sequence: NumberSequence,
    ) -> None:
        """
        Dodaje nową sekwencję (initial current_value).
        """
        ...

    @abstractmethod
    def update(
        self,
        sequence: NumberSequence,
    ) -> None:
        """
        Aktualizuje istniejącą sekwencję.
        """
        ...
