from dataclasses import dataclass
from contract_costs.services.invoices.dto.common import (
    InvoiceUpdate,
    InvoiceLineUpdate,
)

@dataclass(frozen=True)
class CompanyInput:
    name: str
    tax_number: str            # NIP
    street: str | None
    city: str | None
    state: str | None
    zip_code: str | None
    country: str | None
    bank_account: str | None
    role: str | None



@dataclass(frozen=True)
class InvoiceParseResult:
    invoice: InvoiceUpdate
    lines: list[InvoiceLineUpdate]

    buyer: CompanyInput
    seller: CompanyInput
