
import pytest


from contract_costs.repository.inmemory.contract_repository import InMemoryContractRepository
from contract_costs.repository.inmemory.cost_node_repository import InMemoryCostNodeRepository
from contract_costs.repository.inmemory.cost_type_repository import InMemoryCostTypeRepository

from contract_costs.repository.inmemory.invoice_repository import InMemoryInvoiceRepository
from contract_costs.repository.inmemory.invoice_line_repository import InMemoryInvoiceLineRepository
from contract_costs.repository.inmemory.company_repository import InMemoryCompanyRepository

@pytest.fixture(scope="class")
def workflow_context():
    return {
        "invoice_repo": InMemoryInvoiceRepository(),
        "invoice_line_repo": InMemoryInvoiceLineRepository(),
        "company_repo": InMemoryCompanyRepository(),
        "contract_repo": InMemoryContractRepository(),
        "cost_node_repo": InMemoryCostNodeRepository(),
        "cost_type_repo": InMemoryCostTypeRepository(),
    }


class TestWorkflow:

    def test_import_invoice_from_pdf_creates_invoice_and_lines(self,workflow_context):
        # --- services ---
        invoice_repo = workflow_context["invoice_repo"]
        invoice_line_repo = workflow_context["invoice_line_repo"]
        company_repo = workflow_context["company_repo"]
        contract_repo = workflow_context["contract_repo"]
        cost_node_repo = workflow_context["cost_node_repo"]
        cost_type_repo = workflow_context["cost_type_repo"]



