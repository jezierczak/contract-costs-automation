from dataclasses import replace

from contract_costs.model.invoice import InvoiceStatus
from contract_costs.repository.inmemory.invoice_repository import InMemoryInvoiceRepository


class TestInMemoryInvoiceRepository:

    def test_invoice_repository_add_and_get(self, invoice_new):
        repo = InMemoryInvoiceRepository()

        repo.add(invoice_new)
        result = repo.get(invoice_new.id)

        assert result == invoice_new

    def test_invoice_repository_exists(self, invoice_new):
        repo = InMemoryInvoiceRepository()

        assert repo.exists(invoice_new.id) is False

        repo.add(invoice_new)

        assert repo.exists(invoice_new.id) is True

    def test_invoice_repository_list_invoices(
            self,
            invoice_new,
            invoice_processed,
    ):
        repo = InMemoryInvoiceRepository()

        repo.add(invoice_new)
        repo.add(invoice_processed)

        invoices = repo.list_invoices()

        assert len(invoices) == 2
        assert invoice_new in invoices
        assert invoice_processed in invoices

    from dataclasses import replace

    def test_invoice_repository_update(self, invoice_new):
        repo = InMemoryInvoiceRepository()
        repo.add(invoice_new)

        updated = replace(invoice_new, status=InvoiceStatus.IN_PROGRESS)
        repo.update(updated)

        result = repo.get(invoice_new.id)

        assert result.status == InvoiceStatus.IN_PROGRESS

    def test_invoice_repository_get_for_assignment(
            self,
            invoice_new,
            invoice_in_progress,
            invoice_processed,
    ):
        repo = InMemoryInvoiceRepository()

        repo.add(invoice_new)
        repo.add(invoice_in_progress)
        repo.add(invoice_processed)

        result = repo.get_for_assignment()

        assert len(result) == 2
        statuses = {inv.status for inv in result}

        assert InvoiceStatus.NEW in statuses
        assert InvoiceStatus.IN_PROGRESS in statuses
        assert InvoiceStatus.PROCESSED not in statuses



