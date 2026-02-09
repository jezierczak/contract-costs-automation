from abc import ABC, abstractmethod
from typing import Protocol
from uuid import UUID

from contract_costs.model.number_sequence import NumberSequence


class NumberSequenceRepository(ABC):

    @abstractmethod
    def get_for_update(
        self,
        conn,
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
        conn,
        sequence: NumberSequence,
    ) -> None:
        """
        Dodaje nową sekwencję (initial current_value).
        """
        ...

    @abstractmethod
    def save(
        self,
        conn,
        sequence: NumberSequence,
    ) -> None:
        """
        Aktualizuje istniejącą sekwencję.
        """
        ...
