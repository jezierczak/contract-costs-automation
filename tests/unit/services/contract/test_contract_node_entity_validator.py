import pytest
from uuid import uuid4
from contract_costs.services.contracts.validators.contract_node_tree_validator import (
    ContractNodeEntityValidator,
)
from tests.helpers.contracts_helpers import make_contract_node


# -------------------------------------------------
# HAPPY PATH
# -------------------------------------------------

def test_valid_tree_passes():
    validator = ContractNodeEntityValidator()

    contract_id = uuid4()
    org_id = uuid4()

    root = make_contract_node(
        contract_id=contract_id,
        organization_id=org_id,
        code="ROOT",
        parent_id=None,
    )

    child = make_contract_node(
        contract_id=contract_id,
        organization_id=org_id,
        code="1",
        parent_id=root.id,
    )

    validator.validate([root, child])


# -------------------------------------------------
# NO NODES
# -------------------------------------------------

def test_empty_nodes_raises():
    validator = ContractNodeEntityValidator()

    with pytest.raises(ValueError):
        validator.validate([])


# -------------------------------------------------
# MULTIPLE CONTRACT IDS
# -------------------------------------------------

def test_multiple_contract_ids_raises():
    validator = ContractNodeEntityValidator()

    node1 = make_contract_node(contract_id=uuid4(),organization_id= uuid4(), code="ROOT")
    node2 = make_contract_node(contract_id=uuid4(),organization_id= uuid4(), code="1", parent_id=node1.id)

    with pytest.raises(ValueError):
        validator.validate([node1, node2])


# -------------------------------------------------
# DUPLICATE CODES
# -------------------------------------------------

def test_duplicate_codes_raises():
    validator = ContractNodeEntityValidator()

    contract_id = uuid4()
    org_id = uuid4()

    root = make_contract_node(contract_id=contract_id,organization_id= org_id, code= "ROOT")
    child1 = make_contract_node(contract_id=contract_id,organization_id= org_id, code= "1",parent_id= root.id)
    child2 = make_contract_node(contract_id=contract_id,organization_id= org_id, code="1",parent_id= root.id)

    with pytest.raises(ValueError):
        validator.validate([root, child1, child2])


# -------------------------------------------------
# ROOT RULES
# -------------------------------------------------

def test_no_root_raises():
    validator = ContractNodeEntityValidator()

    contract_id = uuid4()
    org_id = uuid4()

    node = make_contract_node(contract_id=contract_id,organization_id= org_id, code= "1", parent_id=uuid4())

    with pytest.raises(ValueError):
        validator.validate([node])


def test_multiple_roots_raises():
    validator = ContractNodeEntityValidator()

    contract_id = uuid4()
    org_id = uuid4()

    root1 = make_contract_node(contract_id=contract_id,organization_id= org_id, code="ROOT")
    root2 = make_contract_node(contract_id=contract_id,organization_id= org_id, code= "ROOT")

    with pytest.raises(ValueError):
        validator.validate([root1, root2])


def test_root_must_have_code_ROOT():
    validator = ContractNodeEntityValidator()

    contract_id = uuid4()
    org_id = uuid4()

    root = make_contract_node(contract_id=contract_id,organization_id= org_id, code= "WRONG")

    with pytest.raises(ValueError):
        validator.validate([root])


# -------------------------------------------------
# PARENT EXISTENCE
# -------------------------------------------------

def test_parent_not_found_raises():
    validator = ContractNodeEntityValidator()

    contract_id = uuid4()
    org_id = uuid4()

    root = make_contract_node(contract_id=contract_id,organization_id= org_id, code= "ROOT")
    child = make_contract_node(contract_id=contract_id,organization_id= org_id, code= "1", parent_id=uuid4())

    with pytest.raises(ValueError):
        validator.validate([root, child])


def test_node_cannot_be_its_own_parent():
    validator = ContractNodeEntityValidator()

    contract_id = uuid4()
    org_id = uuid4()

    node = make_contract_node(contract_id=contract_id,organization_id= org_id, code="ROOT")
    node.parent_id = node.id  # celowo łamiemy zasadę

    with pytest.raises(ValueError):
        validator.validate([node])


# -------------------------------------------------
# CYCLE DETECTION
# -------------------------------------------------

def test_cycle_detection_raises():
    validator = ContractNodeEntityValidator()

    contract_id = uuid4()
    org_id = uuid4()

    root = make_contract_node(contract_id=contract_id,organization_id= org_id,code= "ROOT")
    child = make_contract_node(contract_id=contract_id,organization_id= org_id, code= "1", parent_id=root.id)

    # tworzymy cykl
    root.parent_id = child.id

    with pytest.raises(ValueError):
        validator.validate([root, child])
