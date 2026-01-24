from contract_costs.services.contracts.prepare.contract_node_tree_index import ContractNodeTreeIndex


def test_roots(simple_tree_nodes):
    tree = ContractNodeTreeIndex(simple_tree_nodes)

    roots = tree.roots()

    assert len(roots) == 1
    assert roots[0].code == "ROOT"

def test_children_of(simple_tree_nodes):
    tree = ContractNodeTreeIndex(simple_tree_nodes)

    root = next(n for n in simple_tree_nodes if n.code == "ROOT")
    children = tree.children_of(root.id)

    codes = {c.code for c in children}
    assert codes == {"A", "B"}


def test_is_leaf(simple_tree_nodes):
    tree = ContractNodeTreeIndex(simple_tree_nodes)

    by_code = {n.code: n for n in simple_tree_nodes}

    assert not tree.is_leaf(by_code["ROOT"])
    assert not tree.is_leaf(by_code["A"])

    assert tree.is_leaf(by_code["A1"])
    assert tree.is_leaf(by_code["A2"])
    assert tree.is_leaf(by_code["B"])


def test_leaves(simple_tree_nodes):
    tree = ContractNodeTreeIndex(simple_tree_nodes)

    leaves = tree.leaves()
    codes = {n.code for n in leaves}

    assert codes == {"A1", "A2", "B"}


def test_all_nodes(simple_tree_nodes):
    tree = ContractNodeTreeIndex(simple_tree_nodes)

    all_nodes = tree.all_nodes()

    assert len(all_nodes) == 5
    assert {n.code for n in all_nodes} == {
        "ROOT", "A", "A1", "A2", "B"
    }

def test_postorder(simple_tree_nodes):
    tree = ContractNodeTreeIndex(simple_tree_nodes)

    order = tree.postorder()
    index = {node.code: i for i, node in enumerate(order)}

    # dzieci przed rodzicem
    assert index["A1"] < index["A"]
    assert index["A2"] < index["A"]

    assert index["A"] < index["ROOT"]
    assert index["B"] < index["ROOT"]

def test_empty_tree():
    tree = ContractNodeTreeIndex([])

    assert tree.roots() == []
    assert tree.leaves() == []
    assert tree.all_nodes() == []
    assert tree.postorder() == []
