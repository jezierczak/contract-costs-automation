
import pytest


from contract_costs.repository.inmemory.contract_repository import InMemoryContractRepository
from contract_costs.repository.inmemory.contract_node_repository import InMemoryContractNodeRepository
from contract_costs.repository.inmemory.value_type_repository import InMemoryValueTypeRepository

from contract_costs.repository.inmemory.financial_record_repository import InMemoryFinancialRecordRepository
from contract_costs.repository.inmemory.financial_record_line_repository import InMemoryFinancialRecordLineRepository
from contract_costs.repository.inmemory.company_repository import InMemoryCompanyRepository

@pytest.fixture(scope="class")
def workflow_context():
    return {
        "invoice_repo": InMemoryFinancialRecordRepository(),
        "invoice_line_repo": InMemoryFinancialRecordLineRepository(),
        "company_repo": InMemoryCompanyRepository(),
        "contract_repo": InMemoryContractRepository(),
        "cost_node_repo": InMemoryContractNodeRepository(),
        "cost_type_repo": InMemoryValueTypeRepository(),
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



