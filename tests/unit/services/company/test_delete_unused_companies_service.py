from uuid import uuid4

from contract_costs.model.company import CompanyType
from contract_costs.model.financial_record import FinancialRecordStatus
from contract_costs.services.companies.migration.delete_unused_companies_command import (
    DeleteUnusedCompaniesCommand,
)
from contract_costs.services.companies.migration.delete_unused_companies_service import (
    DeleteUnusedCompaniesService,
)
from tests.builders.company_builder import CompanyBuilder
from tests.builders.contract_builder import ContractBuilder
from tests.builders.financial_record_builder import FinancialRecordBuilder

ORG = uuid4()


def _company(uow, role=CompanyType.SUPPLIER):
    company = (
        CompanyBuilder()
        .with_organization_id(ORG)
        .with_tax_number(uuid4().hex[:10])
        .with_role(role)
        .build()
    )
    uow.companies.add(company)
    return company


def _run(uow, apply=False):
    return DeleteUnusedCompaniesService().execute(
        action=DeleteUnusedCompaniesCommand(organization_id=ORG, actor_user_id=uuid4(), apply=apply),
        uow=uow,
    )


def test_lists_only_companies_without_references(uow):
    own = _company(uow, CompanyType.OWN)
    seller = _company(uow)
    deleted_record_seller = _company(uow)
    client = _company(uow)
    unused = _company(uow)
    uow.financial_records.add(
        FinancialRecordBuilder().with_organization_id(ORG).with_seller_id(seller.id).with_buyer_id(own.id).build()
    )
    uow.financial_records.add(
        FinancialRecordBuilder()
        .with_organization_id(ORG)
        .with_seller_id(deleted_record_seller.id)
        .with_buyer_id(own.id)
        .with_status(FinancialRecordStatus.DELETED)
        .build()
    )
    uow.contracts.add(ContractBuilder().with_organization_id(ORG).with_owner(own).with_client(client).build())

    assert [c.id for c in _run(uow)] == [unused.id]
    assert uow.companies.get(unused.id, ORG) is not None


def test_own_company_is_never_deleted(uow):
    _company(uow, CompanyType.OWN)

    assert _run(uow, apply=True) == []


def test_apply_deletes_unused_companies(uow):
    unused = _company(uow)

    _run(uow, apply=True)

    assert uow.companies.get(unused.id, ORG) is None
