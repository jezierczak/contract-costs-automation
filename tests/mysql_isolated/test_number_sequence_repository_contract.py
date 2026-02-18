import pytest

from contract_costs.common.ids import new_uuid
from contract_costs.model.number_sequence import NumberSequence


def test_number_sequence_add_and_get(number_sequence_repo_contract):
    org_id = new_uuid()
    scope = "invoice"
    seq = NumberSequence.create_initial(organization_id=org_id, scope_key=scope)

    number_sequence_repo_contract.add(seq)

    loaded = number_sequence_repo_contract.get_for_update(
        organization_id=org_id,
        scope_key=scope,
    )
    assert loaded == seq


def test_number_sequence_add_duplicate_raises(number_sequence_repo_contract):
    org_id = new_uuid()
    scope = "invoice"
    seq = NumberSequence.create_initial(organization_id=org_id, scope_key=scope)
    number_sequence_repo_contract.add(seq)

    with pytest.raises(Exception):
        number_sequence_repo_contract.add(seq)


def test_number_sequence_update_existing(number_sequence_repo_contract):
    org_id = new_uuid()
    scope = "invoice"
    seq = NumberSequence.create_initial(organization_id=org_id, scope_key=scope)
    number_sequence_repo_contract.add(seq)

    seq.increase()
    number_sequence_repo_contract.update(seq)

    loaded = number_sequence_repo_contract.get_for_update(
        organization_id=org_id,
        scope_key=scope,
    )
    assert loaded is not None
    assert loaded.current_value == 2


def test_number_sequence_isolated_by_org(number_sequence_repo_contract):
    org_a = new_uuid()
    org_b = new_uuid()
    scope = "invoice"
    seq_a = NumberSequence.create_initial(org_a, scope)
    seq_b = NumberSequence.create_initial(org_b, scope)
    number_sequence_repo_contract.add(seq_a)
    number_sequence_repo_contract.add(seq_b)

    loaded_a = number_sequence_repo_contract.get_for_update(org_a, scope)
    loaded_b = number_sequence_repo_contract.get_for_update(org_b, scope)
    assert loaded_a is not None and loaded_a.organization_id == org_a
    assert loaded_b is not None and loaded_b.organization_id == org_b


def test_number_sequence_isolated_by_scope(number_sequence_repo_contract):
    org_id = new_uuid()
    invoice_seq = NumberSequence.create_initial(org_id, "invoice")
    contract_seq = NumberSequence.create_initial(org_id, "contract")
    number_sequence_repo_contract.add(invoice_seq)
    number_sequence_repo_contract.add(contract_seq)

    loaded_invoice = number_sequence_repo_contract.get_for_update(org_id, "invoice")
    loaded_contract = number_sequence_repo_contract.get_for_update(org_id, "contract")

    assert loaded_invoice is not None and loaded_invoice.scope_key == "invoice"
    assert loaded_contract is not None and loaded_contract.scope_key == "contract"
