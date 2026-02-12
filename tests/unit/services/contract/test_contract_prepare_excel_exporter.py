from pathlib import Path
from uuid import uuid4
from unittest.mock import MagicMock

from contract_costs.services.contracts.prepare.contract_prepare_excel_exporter import ContractPrepareExcelExporter


def test_export_new_creates_empty_sheets(monkeypatch):
    organization_id = uuid4()
    output_path = Path("out.xlsx")

    mock_exporter = MagicMock()

    monkeypatch.setattr(
        "contract_costs.services.contracts.prepare.contract_prepare_excel_exporter.BaseExcelExporter",
        lambda: mock_exporter,
    )

    exporter = ContractPrepareExcelExporter()

    exporter.export_new(
        output_path=output_path,
        organization_id=organization_id,
    )

    assert mock_exporter.add_sheet.call_count == 2
    assert mock_exporter.save.called



def test_export_existing_maps_and_saves(monkeypatch):
    organization_id = uuid4()
    output_path = Path("out.xlsx")

    contract = MagicMock()
    cost_nodes = [MagicMock(), MagicMock()]

    mock_exporter = MagicMock()

    monkeypatch.setattr(
        "contract_costs.services.contracts.prepare.contract_prepare_excel_exporter.BaseExcelExporter",
        lambda: mock_exporter,
    )

    monkeypatch.setattr(
        "contract_costs.services.contracts.prepare.mappers.contract_prepare_mapper.ContractPrepareMapper.map",
        lambda c: MagicMock(),
    )

    monkeypatch.setattr(
        "contract_costs.services.contracts.prepare.mappers.contract_node_prepare_mapper.ContractNodePrepareMapper.map",
        lambda nodes: [MagicMock(), MagicMock()],
    )

    exporter = ContractPrepareExcelExporter()

    exporter.export_existing(
        organization_id=organization_id,
        contract=contract,
        cost_nodes=cost_nodes,
        output_path=output_path,
    )

    assert mock_exporter.add_sheet.call_count == 2
    assert mock_exporter.save.called



def test_export_new_creates_file(tmp_path):
    exporter = ContractPrepareExcelExporter()

    output_path = tmp_path / "test.xlsx"

    exporter.export_new(
        output_path=output_path,
        organization_id=uuid4(),
    )

    assert output_path.exists()
