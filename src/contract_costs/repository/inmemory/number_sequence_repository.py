from threading import Lock
from uuid import UUID

from contract_costs.model.number_sequence import NumberSequence
from contract_costs.repository.number_sequence_repository import (
    NumberSequenceRepository,
)


class InMemoryNumberSequenceRepository(NumberSequenceRepository):

    def __init__(self) -> None:
        self._data: dict[tuple[UUID, str], NumberSequence] = {}
        self._lock = Lock()

    # ---------------------------
    # INTERFACE
    # ---------------------------

    def get_for_update(
        self,
        conn,  # ignorujemy w in-memory
        organization_id: UUID,
        scope_key: str,
    ) -> NumberSequence | None:

        key = (organization_id, scope_key)

        with self._lock:
            sequence = self._data.get(key)
            # Zwracamy referencję – tak jak w realnym repo
            return sequence

    def add(
        self,
        conn,  # ignorujemy
        sequence: NumberSequence,
    ) -> None:

        key = (sequence.organization_id, sequence.scope_key)

        with self._lock:
            if key in self._data:
                raise RuntimeError(
                    "Sequence already exists for this scope"
                )

            self._data[key] = sequence

    def save(
        self,
        conn,  # ignorujemy
        sequence: NumberSequence,
    ) -> None:

        key = (sequence.organization_id, sequence.scope_key)

        with self._lock:
            if key not in self._data:
                raise RuntimeError(
                    "Cannot save non-existing sequence"
                )

            self._data[key] = sequence
