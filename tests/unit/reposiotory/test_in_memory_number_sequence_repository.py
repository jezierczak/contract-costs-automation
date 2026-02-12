from contract_costs.common.ids import new_uuid
from contract_costs.model.number_sequence import NumberSequence


def test_add_and_get_sequence(number_sequence_repo):
    org_id = new_uuid()
    scope = "invoice"

    seq = NumberSequence.create_initial(
        organization_id=org_id,
        scope_key=scope,
    )

    number_sequence_repo.add(None, seq)

    result = number_sequence_repo.get_for_update(
        None,
        organization_id=org_id,
        scope_key=scope,
    )

    assert result == seq

    import pytest

    def test_add_duplicate_sequence_raises(number_sequence_repo):
        org_id = new_uuid()
        scope = "invoice"

        seq = NumberSequence.create_initial(
            organization_id=org_id,
            scope_key=scope,
        )

        number_sequence_repo.add(None, seq)

        with pytest.raises(RuntimeError):
            number_sequence_repo.add(None, seq)

def test_save_existing_sequence(number_sequence_repo):
    org_id = new_uuid()
    scope = "invoice"

    seq = NumberSequence.create_initial(
        organization_id=org_id,
        scope_key=scope,
    )

    number_sequence_repo.add(None, seq)

    seq.increase()
    number_sequence_repo.save(None, seq)

    result = number_sequence_repo.get_for_update(
        None,
        organization_id=org_id,
        scope_key=scope,
    )

    assert result.current_value == 2

import pytest

def test_save_non_existing_raises(number_sequence_repo):
    org_id = new_uuid()
    scope = "invoice"

    seq = NumberSequence.create_initial(
        organization_id=org_id,
        scope_key=scope,
    )

    with pytest.raises(RuntimeError):
        number_sequence_repo.save(None, seq)

def test_sequences_are_isolated_by_org(number_sequence_repo):
    org1 = new_uuid()
    org2 = new_uuid()
    scope = "invoice"

    seq1 = NumberSequence.create_initial(org1, scope)
    seq2 = NumberSequence.create_initial(org2, scope)

    number_sequence_repo.add(None, seq1)
    number_sequence_repo.add(None, seq2)

    result1 = number_sequence_repo.get_for_update(None, org1, scope)
    result2 = number_sequence_repo.get_for_update(None, org2, scope)

    assert result1.organization_id == org1
    assert result2.organization_id == org2


def test_sequences_are_isolated_by_scope(number_sequence_repo):
    org_id = new_uuid()

    invoice_seq = NumberSequence.create_initial(org_id, "invoice")
    contract_seq = NumberSequence.create_initial(org_id, "contract")

    number_sequence_repo.add(None, invoice_seq)
    number_sequence_repo.add(None, contract_seq)

    result_invoice = number_sequence_repo.get_for_update(
        None, org_id, "invoice"
    )

    result_contract = number_sequence_repo.get_for_update(
        None, org_id, "contract"
    )

    assert result_invoice.scope_key == "invoice"
    assert result_contract.scope_key == "contract"

def test_get_for_update_returns_reference(number_sequence_repo):
    org_id = new_uuid()
    scope = "invoice"

    seq = NumberSequence.create_initial(org_id, scope)
    number_sequence_repo.add(None, seq)

    loaded = number_sequence_repo.get_for_update(
        None, org_id, scope
    )

    loaded.increase()

    # Bez save, bo to referencja
    again = number_sequence_repo.get_for_update(
        None, org_id, scope
    )

    assert again.current_value == 2
