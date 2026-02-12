from decimal import Decimal
from datetime import datetime
from typing import Optional
from uuid import UUID

from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now
from contract_costs.model.financial_record_line import FinancialRecordLine
from contract_costs.model.unit_of_measure import UnitOfMeasure
from contract_costs.model.amount import Amount, VatRate, TaxTreatment


class FinancialRecordLineBuilder:
    def __init__(self):
        now = utc_now()

        self._id = new_uuid()
        self._organization_id = new_uuid()
        self._created_at = now
        self._created_by_user_id = None
        self._updated_at = None
        self._updated_by_user_id = None

        self._financial_record_id = None
        self._contract_id = None
        self._contract_node_id = None
        self._value_type_id = None

        self._item_name = "Test Item"
        self._quantity = Decimal("1")
        self._unit = None

        self._amount = Amount(
            value=Decimal("100.00"),
            vat_rate=VatRate.VAT_23,
            tax_treatment=TaxTreatment.TAX_DEDUCTIBLE,
        )

        self._description = None

    # =====================================================
    # BUILD
    # =====================================================

    def build(self) -> FinancialRecordLine:
        return FinancialRecordLine(
            id=self._id,
            organization_id=self._organization_id,
            created_at=self._created_at,
            created_by_user_id=self._created_by_user_id,
            updated_at=self._updated_at,
            updated_by_user_id=self._updated_by_user_id,
            financial_record_id=self._financial_record_id,
            contract_id=self._contract_id,
            contract_node_id=self._contract_node_id,
            value_type_id=self._value_type_id,
            item_name=self._item_name,
            quantity=self._quantity,
            unit=self._unit,
            amount=self._amount,
            description=self._description,
        )

    # =====================================================
    # BASE
    # =====================================================

    def with_id(self, id_: UUID) -> "FinancialRecordLineBuilder":
        self._id = id_
        return self

    def with_organization_id(self, org_id: UUID) -> "FinancialRecordLineBuilder":
        self._organization_id = org_id
        return self

    def with_created_at(self, created_at: datetime) -> "FinancialRecordLineBuilder":
        self._created_at = created_at
        return self

    # =====================================================
    # RELATIONS
    # =====================================================

    def with_financial_record_id(
        self,
        record_id: Optional[UUID],
    ) -> "FinancialRecordLineBuilder":
        self._financial_record_id = record_id
        return self

    def with_contract_id(
        self,
        contract_id: Optional[UUID],
    ) -> "FinancialRecordLineBuilder":
        self._contract_id = contract_id
        return self

    def with_contract_node_id(
        self,
        node_id: Optional[UUID],
    ) -> "FinancialRecordLineBuilder":
        self._contract_node_id = node_id
        return self

    def with_value_type_id(
        self,
        value_type_id: Optional[UUID],
    ) -> "FinancialRecordLineBuilder":
        self._value_type_id = value_type_id
        return self

    # =====================================================
    # BUSINESS DATA
    # =====================================================

    def with_item_name(self, name: str) -> "FinancialRecordLineBuilder":
        self._item_name = name
        return self

    def with_quantity(
        self,
        quantity: Optional[Decimal],
    ) -> "FinancialRecordLineBuilder":
        self._quantity = quantity
        return self

    def with_unit(
        self,
        unit: Optional[UnitOfMeasure],
    ) -> "FinancialRecordLineBuilder":
        self._unit = unit
        return self

    def with_amount(self, amount: Amount) -> "FinancialRecordLineBuilder":
        self._amount = amount
        return self

    def with_description(
        self,
        description: Optional[str],
    ) -> "FinancialRecordLineBuilder":
        self._description = description
        return self
