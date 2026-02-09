from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True)
class NumberSequence:
    organization_id: UUID
    scope_key: str
    current_value: int

    def increase(self) -> int:
        self.current_value += 1
        return self.current_value

    @classmethod
    def create_initial(
            cls,
            organization_id: UUID,
            scope_key: str,
    ) -> "NumberSequence":
        return cls(
            organization_id=organization_id,
            scope_key=scope_key,
            current_value=1,
        )