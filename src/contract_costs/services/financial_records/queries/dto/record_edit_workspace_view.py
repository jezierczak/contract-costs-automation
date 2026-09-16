from dataclasses import dataclass

from contract_costs.services.financial_records.queries.dto.financial_record_edit_view import FinancialRecordEditView

@dataclass(frozen=True)
class WorkspaceContractDTO:
    contract_id: str
    code: str
    name: str | None = None

@dataclass(frozen=True)
class WorkspaceValueTypeDTO:
    id: str
    code: str
    name: str
    direction: str

@dataclass(frozen=True)
class RecordEditWorkspaceView:
    record: FinancialRecordEditView | None

    units: list
    vat_rates: list
    amount_types: list
    tax_treatments: list

    payment_methods: list
    payment_statuses: list

    contracts: list
    agreements: list
    value_types: list
