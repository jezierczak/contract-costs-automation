from dataclasses import replace

from contract_costs.repository.inmemory.invoice_line_repository import InMemoryInvoiceLineRepository


class TestInMemoryInvoiceLineRepository:

    def test_invoice_line_repository_add_and_get(self, invoice_line_complete):
        repo = InMemoryInvoiceLineRepository()

        repo.add(invoice_line_complete)
        result = repo.get(invoice_line_complete.id)

        assert result == invoice_line_complete

    def test_invoice_line_repository_exists(self, invoice_line_complete):
        repo = InMemoryInvoiceLineRepository()

        assert repo.exists(invoice_line_complete.id) is False

        repo.add(invoice_line_complete)

        assert repo.exists(invoice_line_complete.id) is True

    def test_invoice_line_repository_list_lines(
            self,
            invoice_line_complete,
            invoice_line_missing_cost_node,
    ):
        repo = InMemoryInvoiceLineRepository()

        repo.add(invoice_line_complete)
        repo.add(invoice_line_missing_cost_node)

        lines = repo.list_lines()

        assert len(lines) == 2
        assert invoice_line_complete in lines
        assert invoice_line_missing_cost_node in lines

    def test_invoice_line_repository_list_by_contract(
            self,
            invoice_line_complete,
            invoice_line_missing_cost_type,
            contract_id_1,
    ):
        repo = InMemoryInvoiceLineRepository()

        repo.add(invoice_line_complete)  # contract_id_1
        repo.add(invoice_line_missing_cost_type)  # contract_id_2

        result = repo.list_by_contract(contract_id_1)

        assert len(result) == 1
        assert result[0].contract_id == contract_id_1


    def test_invoice_line_repository_update(self, invoice_line_complete):
        repo = InMemoryInvoiceLineRepository()
        repo.add(invoice_line_complete)

        updated = replace(invoice_line_complete, description="Updated")
        repo.update(updated)

        result = repo.get(invoice_line_complete.id)

        assert result.description == "Updated"

    def test_invoice_line_repository_get_for_assignment(
            self,
            invoice_line_complete,
            invoice_line_missing_cost_node,
            invoice_line_missing_cost_type,
    ):
        repo = InMemoryInvoiceLineRepository()

        repo.add(invoice_line_complete)  # OK
        repo.add(invoice_line_missing_cost_node)  # missing cost_node
        repo.add(invoice_line_missing_cost_type)  # missing cost_type

        result = repo.get_for_assignment()

        assert len(result) == 2
        ids = {line.id for line in result}

        assert invoice_line_missing_cost_node.id in ids
        assert invoice_line_missing_cost_type.id in ids
        assert invoice_line_complete.id not in ids




