from contract_costs.common.ids import new_uuid
from tests.builders.financial_record_line_builder import FinancialRecordLineBuilder


def test_add_and_get_line(line_repo):
    org_id = new_uuid()

    line = (
        FinancialRecordLineBuilder()
        .with_organization_id(org_id)
        .build()
    )

    line_repo.add(
        organization_id=org_id,
        line=line,
    )

    result = line_repo.get(
        organization_id=org_id,
        line_id=line.id,
    )

    assert result == line


def test_get_isolated_by_org(line_repo):
    org1 = new_uuid()
    org2 = new_uuid()

    line = (
        FinancialRecordLineBuilder()
        .with_organization_id(org1)
        .build()
    )

    line_repo.add(organization_id=org1, line=line)

    assert line_repo.get(
        organization_id=org2,
        line_id=line.id,
    ) is None


def test_list_by_financial_record(line_repo):
    org_id = new_uuid()
    record_id = new_uuid()

    line = (
        FinancialRecordLineBuilder()
        .with_organization_id(org_id)
        .with_financial_record_id(record_id)
        .build()
    )

    line_repo.add(organization_id=org_id, line=line)

    result = line_repo.list_by_financial_record(
        organization_id=org_id,
        financial_record_id=record_id,
    )

    assert result == [line]

def test_list_unassigned(line_repo):
    org_id = new_uuid()

    assigned = (
        FinancialRecordLineBuilder()
        .with_organization_id(org_id)
        .with_financial_record_id(new_uuid())
        .build()
    )

    unassigned = (
        FinancialRecordLineBuilder()
        .with_organization_id(org_id)
        .with_financial_record_id(None)
        .build()
    )

    line_repo.add(organization_id=org_id, line=assigned)
    line_repo.add(organization_id=org_id, line=unassigned)

    result = line_repo.list_unassigned(organization_id=org_id)

    assert result == [unassigned]

def test_list_by_contract(line_repo):
    org_id = new_uuid()
    contract_id = new_uuid()

    line = (
        FinancialRecordLineBuilder()
        .with_organization_id(org_id)
        .with_contract_id(contract_id)
        .build()
    )

    line_repo.add(organization_id=org_id, line=line)

    result = line_repo.list_by_contract(
        organization_id=org_id,
        contract_id=contract_id,
    )

    assert result == [line]


from datetime import date, datetime


def test_list_by_contract_until_filters_by_date(line_repo):
    org_id = new_uuid()
    contract_id = new_uuid()

    old_line = (
        FinancialRecordLineBuilder()
        .with_organization_id(org_id)
        .with_contract_id(contract_id)
        .with_created_at(datetime(2024, 1, 1))
        .build()
    )

    new_line = (
        FinancialRecordLineBuilder()
        .with_organization_id(org_id)
        .with_contract_id(contract_id)
        .with_created_at(datetime(2025, 1, 1))
        .build()
    )

    line_repo.add(organization_id=org_id, line=old_line)
    line_repo.add(organization_id=org_id, line=new_line)

    result = line_repo.list_by_contract_until(
        organization_id=org_id,
        contract_id=contract_id,
        snapshot_date=date(2024, 6, 1),
    )

    assert result == [old_line]


def test_delete_not_in_ids(line_repo):
    org_id = new_uuid()
    record_id = new_uuid()

    l1 = (
        FinancialRecordLineBuilder()
        .with_organization_id(org_id)
        .with_financial_record_id(record_id)
        .build()
    )

    l2 = (
        FinancialRecordLineBuilder()
        .with_organization_id(org_id)
        .with_financial_record_id(record_id)
        .build()
    )

    line_repo.add(organization_id=org_id, line=l1)
    line_repo.add(organization_id=org_id, line=l2)

    deleted = line_repo.delete_not_in_ids(
        organization_id=org_id,
        financial_record_id=record_id,
        keep_ids={l1.id},
    )

    assert deleted == 1
    assert line_repo.exists(
        organization_id=org_id,
        line_id=l1.id,
    )
    assert not line_repo.exists(
        organization_id=org_id,
        line_id=l2.id,
    )
