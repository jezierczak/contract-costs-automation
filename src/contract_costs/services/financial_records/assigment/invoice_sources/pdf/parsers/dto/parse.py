from dataclasses import dataclass

from contract_costs.model.document import DocumentType
from contract_costs.services.financial_records.assigment.invoice_sources.dto.common import (
    FinancialRecordUpdate,
    FinancialRecordLineUpdate, )

@dataclass(frozen=True)
class CompanyInput:
    name: str | None
    tax_number: str | None           # NIP
    street: str | None
    city: str | None
    state: str | None
    zip_code: str | None
    country: str | None
    phone_number: str | None
    email: str | None
    bank_account: str | None
    role: str



@dataclass(frozen=True)
class DocumentParseResult:
    document_type: DocumentType
    record: FinancialRecordUpdate
    lines: list[FinancialRecordLineUpdate]

    buyer: CompanyInput
    seller: CompanyInput
