import uuid
from datetime import date, datetime
from decimal import Decimal

from contract_costs.model.amount import Amount, VatRate
from contract_costs.model.invoice_line import InvoiceLine
from contract_costs.services.snapshots.create_contract_snapshot_service import CreateContractSnapshotService


def test_snapshot_created(repos):
    (
        contract,
        contract_repo,
        node_repo,
        invoice_repo,
        snapshot_repo,
        node_snapshot_repo,
        value_snapshot_repo,
    ) = repos

    service = CreateContractSnapshotService(
        contract_repo=contract_repo,
        contract_node_repo=node_repo,
        invoice_line_repo=invoice_repo,
        snapshot_repo=snapshot_repo,
        node_snapshot_repo=node_snapshot_repo,
        value_snapshot_repo=value_snapshot_repo,
    )

    snapshot = service.create(
        contract_id=contract.id,
        snapshot_date=date(2024, 1, 1),
    )

    assert snapshot.contract_id == contract.id
    assert len(snapshot_repo.list_all()) == 1

def test_weighted_progress(repos):
    (
        contract,
        _,
        node_repo,
        invoice_repo,
        snapshot_repo,
        node_snapshot_repo,
        value_snapshot_repo,
    ) = repos

    service = CreateContractSnapshotService(
        contract_repo=_,
        contract_node_repo=node_repo,
        invoice_line_repo=invoice_repo,
        snapshot_repo=snapshot_repo,
        node_snapshot_repo=node_snapshot_repo,
        value_snapshot_repo=value_snapshot_repo,
    )

    service.create(
        contract_id=contract.id,
        snapshot_date=date(2024, 1, 1),
    )

    by_node = {
        s.contract_node_id: s
        for s in node_snapshot_repo.list_all()
    }

    a = node_repo.get_by_code("A")
    progress = by_node[a.id].progress

    assert progress.quantize(Decimal("0.0001")) == Decimal("0.3333")

def test_costs_aggregated(repos):
    (
        contract,
        _,
        node_repo,
        invoice_repo,
        snapshot_repo,
        node_snapshot_repo,
        value_snapshot_repo,
    ) = repos

    vt_cost = uuid.uuid4()

    invoice_repo._add_with_created_at(
        InvoiceLine(
            id=uuid.uuid4(),
            invoice_id=None,
            contract_id=contract.id,
            contract_node_id=node_repo.get_by_code("A1").id,
            value_type_id=vt_cost,
            item_name="Work A1",
            quantity=None,
            unit=None,
            amount=Amount(Decimal("50"), VatRate.VAT_0),
            description=None,
        ),
        created_at=datetime(2023, 12, 31, 12, 0),
    )

    invoice_repo._add_with_created_at(
        InvoiceLine(
            id=uuid.uuid4(),
            invoice_id=None,
            contract_id=contract.id,
            contract_node_id=node_repo.get_by_code("A2").id,
            value_type_id=vt_cost,
            item_name="Work A2",
            quantity=None,
            unit=None,
            amount=Amount(Decimal("30"), VatRate.VAT_0),
            description=None,
        ),
        created_at=datetime(2023, 12, 31, 13, 0),
    )

    service = CreateContractSnapshotService(
        contract_repo=_,
        contract_node_repo=node_repo,
        invoice_line_repo=invoice_repo,
        snapshot_repo=snapshot_repo,
        node_snapshot_repo=node_snapshot_repo,
        value_snapshot_repo=value_snapshot_repo,
    )

    service.create(
        contract_id=contract.id,
        snapshot_date=date(2024, 1, 1),
    )

    leaf_node_ids = {
        node_repo.get_by_code("A1").id,
        node_repo.get_by_code("A2").id,
    }

    snapshots = value_snapshot_repo.list_all()

    assert sum(
        v.net
        for v in snapshots
        if node_snapshot_repo.get(v.node_snapshot_id).contract_node_id in leaf_node_ids
    ) == Decimal("80")

