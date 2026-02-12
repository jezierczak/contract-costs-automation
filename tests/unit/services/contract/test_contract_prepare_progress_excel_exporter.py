from pathlib import Path
from uuid import uuid4
from unittest.mock import MagicMock

from contract_costs.services.contracts.prepare.contract_prepare_progress_excel_exporter import (
    ContractPrepareProgressExcelExporter,
)


def test_export_existing_adds_sheet_and_saves(monkeypatch):
    organization_id = uuid4()
    output_path = Path("out.xlsx")

    contract = MagicMock()
    cost_nodes = [MagicMock(), MagicMock()]

    mock_exporter = MagicMock()

    # 🔥 patch we właściwym miejscu
    monkeypatch.setattr(
        "contract_costs.services.contracts.prepare.contract_prepare_progress_excel_exporter.BaseExcelExporter",
        lambda: mock_exporter,
    )

    # mock mappera
    monkeypatch.setattr(
        "contract_costs.services.contracts.prepare.mappers.contract_node_progress_prepare_mapper.ContractNodeProgressPrepareMapper.map",
        lambda contract, nodes: [MagicMock(), MagicMock()],
    )

    exporter = ContractPrepareProgressExcelExporter()

    exporter.export_existing(
        organization_id=organization_id,
        contract=contract,
        cost_nodes=cost_nodes,
        output_path=output_path,
    )

    # ✅ sprawdzamy czy add_sheet wywołane
    assert mock_exporter.add_sheet.call_count == 1

    # ✅ sprawdzamy czy save wywołane
    mock_exporter.save.assert_called_once_with(output_path)
