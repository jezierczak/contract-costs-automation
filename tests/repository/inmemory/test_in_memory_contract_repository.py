from uuid import uuid4

from contract_costs.repository.inmemory.contract_repository import InMemoryContractRepository
from contract_costs.model.contract import Contract
from contract_costs.repository.inmemory.invoice_line_repository import InMemoryInvoiceLineRepository


class TestInMemoryContractRepository:

    def test_inmemory_contract_repository_add_and_get(self,contract_1: Contract) -> None:
        repo = InMemoryContractRepository()

        repo.add(contract_1)

        result = repo.get(contract_1.id)

        assert result == contract_1

    def test_inmemory_contract_repository_list(self,contract_1, contract_2) -> None:
        repo = InMemoryContractRepository()

        repo.add(contract_1)
        repo.add(contract_2)

        result = repo.list()

        assert len(result) == 2
        assert contract_1 in result
        assert contract_2 in result

    def test_inmemory_contract_repository_exists(self,contract_1) -> None:
        repo = InMemoryContractRepository()

        assert repo.exists(contract_1.id) is False

        repo.add(contract_1)

        assert repo.exists(contract_1.id) is True

    def test_invoice_line_repository_list_by_contract(
            self,
            contract_1,
            contract_2,
            invoice_line_1,
            invoice_line_2,
    ):
        repo = InMemoryInvoiceLineRepository()

        repo.add(invoice_line_1)  # contract_1
        repo.add(invoice_line_2)  # contract_2

        result = repo.list_by_contract(contract_1.id)

        assert len(result) == 1
        assert result[0].contract_id == contract_1.id


