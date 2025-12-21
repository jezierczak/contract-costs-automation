from uuid import uuid4

from contract_costs.model.cost_type import CostType
from contract_costs.repository.cost_type_repository import CostTypeRepository


class CreateCostTypeService:

    def __init__(self, repository: CostTypeRepository) -> None:
        self._repository = repository

    def execute(
        self,
        *,
        code: str,
        name: str,
        description: str | None,
        is_active: bool,
    ) -> None:
        # --- uniqueness check ---
        existing = self._repository.get_by_code(code)
        if existing:
            raise ValueError(f"CostType with code '{code}' already exists")

        cost_type = CostType(
            id=uuid4(),
            code=code,
            name=name,
            description=description,
            is_active=is_active,
        )

        self._repository.add(cost_type)
