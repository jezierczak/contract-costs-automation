from uuid import uuid4

from contract_costs.model.value_direction import ValueDirection
from contract_costs.model.value_type import ValueType
from contract_costs.repository.value_type_repository import ValueTypeRepository


class CreateValueTypeService:

    def __init__(self, repository: ValueTypeRepository) -> None:
        self._repository = repository

    def execute(
        self,
        *,
        code: str,
        name: str,
        description: str | None,
        direction: ValueDirection,
        is_active: bool,
    ) -> None:
        # --- uniqueness check ---
        existing = self._repository.get_by_code(code)
        if existing:
            raise ValueError(f"ValueType with code '{code}' already exists")

        value_type = ValueType(
            id=uuid4(),
            code=code,
            name=name,
            description=description,
            direction=direction,
            is_active=is_active,
        )

        self._repository.add(value_type)
