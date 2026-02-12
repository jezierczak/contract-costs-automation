from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now
from contract_costs.model.value_type import ValueType
from contract_costs.model.value_direction import ValueDirection


class ValueTypeBuilder:
    def __init__(self):
        now = utc_now()

        self._id = new_uuid()
        self._organization_id = new_uuid()
        self._created_at = now
        self._created_by_user_id = None
        self._updated_at = None
        self._updated_by_user_id = None

        self._code = "MATERIAL"
        self._name = "Material"
        self._description = None
        self._direction = ValueDirection.COST
        self._is_active = True

    def build(self) -> ValueType:
        return ValueType(
            id=self._id,
            organization_id=self._organization_id,
            created_at=self._created_at,
            created_by_user_id=self._created_by_user_id,
            updated_at=self._updated_at,
            updated_by_user_id=self._updated_by_user_id,
            code=self._code,
            name=self._name,
            description=self._description,
            direction=self._direction,
            is_active=self._is_active,
        )

    def with_organization_id(self, org_id):
        self._organization_id = org_id
        return self

    def with_code(self, code):
        self._code = code
        return self

    def with_direction(self, direction):
        self._direction = direction
        return self

    def with_is_active(self, is_active: bool):
        self._is_active = is_active
        return self
