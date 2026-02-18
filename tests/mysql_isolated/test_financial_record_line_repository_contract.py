from datetime import date, datetime

from contract_costs.common.ids import new_uuid
from tests.builders.financial_record_line_builder import FinancialRecordLineBuilder


def _assert_same_line(actual, expected):
    assert actual is not None
    assert actual.id == expected.id
    assert actual.organization_id == expected.organization_id
    assert actual.financial_record_id == expected.financial_record_id
    assert actual.contract_id == expected.contract_id
    assert actual.contract_node_id == expected.contract_node_id
    assert actual.value_type_id == expected.value_type_id
    assert actual.item_name == expected.item_name
    assert actual.quantity == expected.quantity
    assert actual.unit == expected.unit
    assert actual.amount.value == expected.amount.value
    assert actual.amount.vat_rate == expected.amount.vat_rate
    assert actual.amount.tax_treatment == expected.amount.tax_treatment
    assert actual.description == expected.description


def test_financial_record_line_add_and_get(financial_record_line_repo_contract):
    org_id = new_uuid()
    line = FinancialRecordLineBuilder().with_organization_id(org_id).build()

    financial_record_line_repo_contract.add(organization_id=org_id, line=line)

    loaded = financial_record_line_repo_contract.get(
        organization_id=org_id,
        line_id=line.id,
    )
    _assert_same_line(loaded, line)


def test_financial_record_line_get_isolation_by_org(financial_record_line_repo_contract):
    org_a = new_uuid()
    org_b = new_uuid()
    line = FinancialRecordLineBuilder().with_organization_id(org_a).build()
    financial_record_line_repo_contract.add(organization_id=org_a, line=line)

    loaded = financial_record_line_repo_contract.get(
        organization_id=org_b,
        line_id=line.id,
    )
    assert loaded is None


def test_financial_record_line_list_by_financial_record(financial_record_line_repo_contract):
    org_id = new_uuid()
    record_id = new_uuid()
    line = (
        FinancialRecordLineBuilder()
        .with_organization_id(org_id)
        .with_financial_record_id(record_id)
        .build()
    )
    financial_record_line_repo_contract.add(organization_id=org_id, line=line)

    listed = financial_record_line_repo_contract.list_by_financial_record(
        organization_id=org_id,
        financial_record_id=record_id,
    )
    assert [l.id for l in listed] == [line.id]


def test_financial_record_line_list_unassigned(financial_record_line_repo_contract):
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
    financial_record_line_repo_contract.add(organization_id=org_id, line=assigned)
    financial_record_line_repo_contract.add(organization_id=org_id, line=unassigned)

    listed = financial_record_line_repo_contract.list_unassigned(organization_id=org_id)
    assert [l.id for l in listed] == [unassigned.id]


def test_financial_record_line_list_by_contract_until(financial_record_line_repo_contract):
    org_id = new_uuid()
    contract_id = new_uuid()
    old_line = (
        FinancialRecordLineBuilder()
        .with_organization_id(org_id)
        .with_contract_id(contract_id)
        .with_created_at(datetime(2026, 1, 1))
        .build()
    )
    new_line = (
        FinancialRecordLineBuilder()
        .with_organization_id(org_id)
        .with_contract_id(contract_id)
        .with_created_at(datetime(2026, 2, 1))
        .build()
    )
    financial_record_line_repo_contract.add(organization_id=org_id, line=old_line)
    financial_record_line_repo_contract.add(organization_id=org_id, line=new_line)

    listed = financial_record_line_repo_contract.list_by_contract_until(
        organization_id=org_id,
        contract_id=contract_id,
        snapshot_date=date(2026, 1, 15),
    )
    assert [l.id for l in listed] == [old_line.id]


def test_financial_record_line_delete_not_in_ids(financial_record_line_repo_contract):
    org_id = new_uuid()
    record_id = new_uuid()
    keep = (
        FinancialRecordLineBuilder()
        .with_organization_id(org_id)
        .with_financial_record_id(record_id)
        .build()
    )
    drop = (
        FinancialRecordLineBuilder()
        .with_organization_id(org_id)
        .with_financial_record_id(record_id)
        .build()
    )
    financial_record_line_repo_contract.add(organization_id=org_id, line=keep)
    financial_record_line_repo_contract.add(organization_id=org_id, line=drop)

    deleted = financial_record_line_repo_contract.delete_not_in_ids(
        organization_id=org_id,
        financial_record_id=record_id,
        keep_ids={keep.id},
    )

    assert deleted == 1
    assert financial_record_line_repo_contract.exists(organization_id=org_id, line_id=keep.id)
    assert not financial_record_line_repo_contract.exists(organization_id=org_id, line_id=drop.id)


def test_financial_record_line_update_and_list_helpers(financial_record_line_repo_contract):
    org_id = new_uuid()
    contract_id = new_uuid()
    record_id = new_uuid()
    line = (
        FinancialRecordLineBuilder()
        .with_organization_id(org_id)
        .with_financial_record_id(record_id)
        .with_contract_id(contract_id)
        .build()
    )
    financial_record_line_repo_contract.add(organization_id=org_id, line=line)

    line.item_name = "Updated item"
    financial_record_line_repo_contract.update(organization_id=org_id, line=line)

    loaded = financial_record_line_repo_contract.get(organization_id=org_id, line_id=line.id)
    assert loaded is not None
    assert loaded.item_name == "Updated item"

    assert {l.id for l in financial_record_line_repo_contract.list_all(organization_id=org_id)} == {line.id}
    assert [l.id for l in financial_record_line_repo_contract.list_by_contract(organization_id=org_id, contract_id=contract_id)] == [line.id]
    assert [l.id for l in financial_record_line_repo_contract.list_by_financial_record_ids(
        organization_id=org_id,
        financial_records_ids=[record_id],
    )] == [line.id]
    assert financial_record_line_repo_contract.list_by_financial_record_ids(
        organization_id=org_id,
        financial_records_ids=[],
    ) == []


def test_financial_record_line_null_invoice_and_assignment_filters(financial_record_line_repo_contract):
    org_id = new_uuid()
    missing_assignment = (
        FinancialRecordLineBuilder()
        .with_organization_id(org_id)
        .with_financial_record_id(new_uuid())
        .with_contract_node_id(None)
        .build()
    )
    null_invoice = (
        FinancialRecordLineBuilder()
        .with_organization_id(org_id)
        .with_financial_record_id(None)
        .build()
    )
    financial_record_line_repo_contract.add(organization_id=org_id, line=missing_assignment)
    financial_record_line_repo_contract.add(organization_id=org_id, line=null_invoice)

    if hasattr(financial_record_line_repo_contract, "list_by_null_invoice"):
        assert [
            l.id
            for l in financial_record_line_repo_contract.list_by_null_invoice(organization_id=org_id)
        ] == [null_invoice.id]
    else:
        assert [
            l.id
            for l in financial_record_line_repo_contract.list_unassigned(organization_id=org_id)
        ] == [null_invoice.id]
    if hasattr(financial_record_line_repo_contract, "get_for_assignment"):
        ids_for_assignment = {
            l.id
            for l in financial_record_line_repo_contract.get_for_assignment(
                organization_id=org_id
            )
        }
        assert missing_assignment.id in ids_for_assignment


def test_financial_record_line_delete_not_in_ids_when_keep_empty(financial_record_line_repo_contract):
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
    financial_record_line_repo_contract.add(organization_id=org_id, line=l1)
    financial_record_line_repo_contract.add(organization_id=org_id, line=l2)

    deleted = financial_record_line_repo_contract.delete_not_in_ids(
        organization_id=org_id,
        financial_record_id=record_id,
        keep_ids=set(),
    )
    assert deleted == 2
