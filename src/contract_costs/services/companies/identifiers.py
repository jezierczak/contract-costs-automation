import re
from datetime import datetime
from uuid import UUID

from contract_costs.common.ids import new_uuid
from contract_costs.model.company import Address, Company, CompanyType, CompanyVerificationStatus
from contract_costs.services.common.resolve_utils import (
    OTHER_IDENTIFIER_PREFIX,
    UNKNOWN_BUYER_ID,
    UNKNOWN_SELLER_ID,
)
from contract_costs.unit_of_work import UnitOfWork

_OTHER_IDENTIFIER = re.compile(rf"^{re.escape(OTHER_IDENTIFIER_PREFIX)}(\d+)$")

_UNKNOWN_COMPANIES = {
    UNKNOWN_SELLER_ID: ("Nieznany sprzedawca", CompanyType.SELLER),
    UNKNOWN_BUYER_ID: ("Nieznany nabywca", CompanyType.BUYER),
}


def next_other_identifier(*, uow: UnitOfWork, organization_id: UUID) -> str:
    """
    Kolejny identyfikator dla kontrahenta bez NIP-u (osoba prywatna, pracownik…):
    OTH-000001, OTH-000002… – najwyższy istniejący w organizacji + 1.
    Nic nie zapisuje; kolizję przy równoczesnym zapisie łapie unikalność tax_number.
    """
    numbers = [
        int(m.group(1))
        for company in uow.companies.list_all(organization_id)
        if (m := _OTHER_IDENTIFIER.match(company.tax_number or ""))
    ]
    return f"{OTHER_IDENTIFIER_PREFIX}{max(numbers, default=0) + 1:06d}"


def unknown_company(
    *,
    uow: UnitOfWork,
    organization_id: UUID,
    actor_user_id: UUID,
    buyer: bool,
    now: datetime,
) -> Company:
    """
    Wspólna firma dla nierozpoznanych kontrahentów (UNKNOWN_SELLER / UNKNOWN_BUYER),
    zakładana przy pierwszym użyciu. Zawsze TO_VERIFY – rekord z nią nie przejdzie
    walidacji, dopóki użytkownik nie przepnie go na właściwą firmę.
    """
    tax_number = UNKNOWN_BUYER_ID if buyer else UNKNOWN_SELLER_ID
    existing = uow.companies.get_by_tax_number(tax_number, organization_id)
    if existing:
        return existing

    name, role = _UNKNOWN_COMPANIES[tax_number]
    company = Company(
        id=new_uuid(),
        organization_id=organization_id,
        name=name,
        description="Wspólna firma dla nierozpoznanych kontrahentów – przepnij rekord na właściwą firmę",
        tax_number=tax_number,
        address=Address(street="", city="", zip_code="", country=""),
        contact=None,
        bank_account=None,
        role=role,
        tags=set(),
        is_active=True,
        verification_status=CompanyVerificationStatus.TO_VERIFY,
        created_at=now,
        created_by_user_id=actor_user_id,
        updated_at=None,
        updated_by_user_id=None,
    )
    uow.companies.add(company)
    return company
