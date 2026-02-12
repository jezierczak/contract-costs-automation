from uuid import uuid4

from contract_costs.services.contracts.prepare.contract_node_tree_index import ContractNodeTreeIndex
from tests.helpers.contracts_helpers import make_contract_node


# --------------------------------------------------
# BASIC STRUCTURE
# --------------------------------------------------

def test_roots_and_children():
    contract_id = uuid4()
    org_id = uuid4()

    root = make_contract_node(contract_id=contract_id, organization_id=org_id, code="ROOT")
    child1 = make_contract_node(contract_id=contract_id, organization_id=org_id, code="1", parent_id=root.id)
    child2 = make_contract_node(contract_id=contract_id, organization_id=org_id, code="2", parent_id=root.id)

    index = ContractNodeTreeIndex([root, child1, child2])

    assert index.roots() == [root]
    # assert set(index.children_of(root.id)) == {child1, child2}
    assert len(index.children_of(root.id)) == 2
    assert child1 in index.children_of(root.id)
    assert child2 in index.children_of(root.id)
    assert index.is_leaf(child1)
    assert not index.is_leaf(root)


# --------------------------------------------------
# LEAVES
# --------------------------------------------------

def test_leaves():
    contract_id = uuid4()
    org_id = uuid4()

    root = make_contract_node(contract_id=contract_id, organization_id=org_id, code="ROOT")
    child = make_contract_node(contract_id=contract_id, organization_id=org_id, code="1", parent_id=root.id)
    leaf = make_contract_node(contract_id=contract_id, organization_id=org_id, code="1.1", parent_id=child.id)

    index = ContractNodeTreeIndex([root, child, leaf])

    leaves = index.leaves()

    assert leaves == [leaf]


# --------------------------------------------------
# POSTORDER
# --------------------------------------------------

def test_postorder_traversal():
    contract_id = uuid4()
    org_id = uuid4()

    root = make_contract_node(contract_id=contract_id, organization_id=org_id, code="ROOT")
    child1 = make_contract_node(contract_id=contract_id, organization_id=org_id, code="1", parent_id=root.id)
    child2 = make_contract_node(contract_id=contract_id, organization_id=org_id, code="2", parent_id=root.id)

    index = ContractNodeTreeIndex([root, child1, child2])

    order = index.postorder()

    # dzieci najpierw, potem root
    assert order[-1] == root
    assert child1 in order
    assert child2 in order


# --------------------------------------------------
# SORTING BY CODE
# --------------------------------------------------

def test_children_sorted_by_code():
    contract_id = uuid4()
    org_id = uuid4()

    root = make_contract_node(contract_id=contract_id, organization_id=org_id, code="ROOT")
    child_b = make_contract_node(contract_id=contract_id, organization_id=org_id, code="B", parent_id=root.id)
    child_a = make_contract_node(contract_id=contract_id, organization_id=org_id, code="A", parent_id=root.id)

    index = ContractNodeTreeIndex([root, child_b, child_a])

    children = index.children_of(root.id)

    assert children[0].code == "A"
    assert children[1].code == "B"


# --------------------------------------------------
# MULTIPLE ROOTS
# --------------------------------------------------

def test_multiple_roots():
    contract_id = uuid4()
    org_id = uuid4()

    root1 = make_contract_node(contract_id=contract_id, organization_id=org_id, code="ROOT")
    root2 = make_contract_node(contract_id=contract_id, organization_id=org_id, code="ROOT2")

    index = ContractNodeTreeIndex([root1, root2])

    # assert set(index.roots()) == {root1, root2}
    assert len(index.roots()) == 2
    assert root1 in index.roots()
    assert root2 in index.roots()


# --------------------------------------------------
# EMPTY INDEX
# --------------------------------------------------

def test_empty_index():
    index = ContractNodeTreeIndex([])

    assert index.roots() == []
    assert index.leaves() == []
    assert index.postorder() == []
    assert index.all_nodes() == []


# --------------------------------------------------
# SINGLE NODE TREE
# --------------------------------------------------

def test_single_node_tree():
    contract_id = uuid4()
    org_id = uuid4()

    root = make_contract_node(contract_id=contract_id, organization_id=org_id, code="ROOT")

    index = ContractNodeTreeIndex([root])

    assert index.roots() == [root]
    assert index.leaves() == [root]
    assert index.postorder() == [root]
    assert index.is_leaf(root)
