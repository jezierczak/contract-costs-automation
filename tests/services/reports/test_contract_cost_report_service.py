from decimal import Decimal

from contract_costs.repository.inmemory.contract_repository import InMemoryContractRepository
from contract_costs.repository.inmemory.cost_node_repository import InMemoryCostNodeRepository
from contract_costs.repository.inmemory.cost_type_repository import InMemoryCostTypeRepository
from contract_costs.repository.inmemory.invoice_line_repository import InMemoryInvoiceLineRepository
from contract_costs.repository.inmemory.invoice_repository import InMemoryInvoiceRepository
from contract_costs.services.reports.contract_cost_report_service import ContractCostReportService


def test_contract_cost_report_returns_leaf_costs(
    report_service,
    contract,
):
    rows = report_service.generate_rows(contract.id)

    assert len(rows) == 1

    row = rows[0]
    assert row["cost_node_code"] == "MAT"
    assert row["cost_type_code"] == "MATERIAL"
    assert row["net_amount"] == Decimal("100")
    assert row["vat_amount"] == Decimal("23.00")
    assert row["gross_amount"] == Decimal("123.00")

def test_contract_cost_report_empty_when_no_invoice_lines(contract):
    contract_repo = InMemoryContractRepository()
    contract_repo.add(contract)

    service = ContractCostReportService(
        contract_repo,
        InMemoryInvoiceLineRepository(),
        InMemoryCostNodeRepository(),
        InMemoryCostTypeRepository(),
    )

    rows = service.generate_rows(contract.id)
    assert rows == []

