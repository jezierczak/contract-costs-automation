from datetime import datetime

from contract_costs.common.ids import new_uuid
from contract_costs.model.company import CompanyVerificationStatus
from contract_costs.services.common.resolve_utils import normalize_required_tax_number
from contract_costs.services.companies.identifiers import next_other_identifier, unknown_company
from contract_costs.services.companies.validators.company import CompanyValidator
from tests.builders.company_builder import CompanyBuilder


def test_next_other_identifier_starts_at_one(uow):
    assert next_other_identifier(uow=uow, organization_id=new_uuid()) == "OTH-000001"


def test_next_other_identifier_follows_highest_existing(company_repo, uow):
    org_id = new_uuid()
    for tax in ("OTH-000003", "OTH-000011", "5261009959", "TMP-abcd"):
        company_repo.add(CompanyBuilder().with_organization_id(org_id).with_tax_number(tax).build())
    # inna organizacja nie wpływa na numerację
    company_repo.add(CompanyBuilder().with_organization_id(new_uuid()).with_tax_number("OTH-000050").build())

    assert next_other_identifier(uow=uow, organization_id=org_id) == "OTH-000012"


def test_unknown_company_is_created_once_per_side(uow):
    org_id = new_uuid()
    kwargs = dict(uow=uow, organization_id=org_id, actor_user_id=new_uuid(), now=datetime(2026, 9, 26))

    seller = unknown_company(buyer=False, **kwargs)
    buyer = unknown_company(buyer=True, **kwargs)

    assert seller.tax_number == "UNKNOWN_SELLER"
    assert buyer.tax_number == "UNKNOWN_BUYER"
    assert unknown_company(buyer=False, **kwargs).id == seller.id
    assert seller.verification_status == CompanyVerificationStatus.TO_VERIFY


def test_other_identifier_is_trusted_and_kept_as_is():
    assert CompanyValidator.is_trusted_tax_number("OTH-000001") is True
    assert CompanyValidator.is_trusted_tax_number("UNKNOWN_SELLER") is False
    assert normalize_required_tax_number(" OTH-000001 ") == "OTH-000001"
    assert normalize_required_tax_number("UNKNOWN_BUYER") == "UNKNOWN_BUYER"


def test_pesel_with_valid_checksum_is_trusted():
    assert CompanyValidator.validate_pesel("44051401359") is True
    assert CompanyValidator.is_trusted_tax_number("44051401359") is True
    assert CompanyValidator.is_trusted_tax_number("44051401358") is False   # zła suma
    assert CompanyValidator.is_trusted_tax_number("4405140135") is False    # 10 cyfr, zły NIP
