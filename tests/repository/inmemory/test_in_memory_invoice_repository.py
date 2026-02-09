from dataclasses import replace

from contract_costs.model.financial_record import FinancialRecordStatus
from contract_costs.repository.inmemory.financial_record_repository import InMemoryFinancialRecordRepository


class TestInMemoryInvoiceRepository:

    def test_invoice_repository_add_and_get(self, invoice_new):
        repo = InMemoryFinancialRecordRepository()

        repo.add(invoice_new)
        result = repo.get(invoice_new.id)

        assert result == invoice_new

    def test_invoice_repository_exists(self, invoice_new):
        repo = InMemoryFinancialRecordRepository()

        assert repo.exists(invoice_new.id) is False

        repo.add(invoice_new)

        assert repo.exists(invoice_new.id) is True

    def test_invoice_repository_list_invoices(
            self,
            invoice_new,
            invoice_processed,
    ):
        repo = InMemoryFinancialRecordRepository()

        repo.add(invoice_new)
        repo.add(invoice_processed)

        invoices = repo.list_all()

        assert len(invoices) == 2
        assert invoice_new in invoices
        assert invoice_processed in invoices

    from dataclasses import replace

    def test_invoice_repository_update(self, invoice_new):
        repo = InMemoryFinancialRecordRepository()
        repo.add(invoice_new)

        updated = replace(invoice_new, status=FinancialRecordStatus.IN_PROGRESS)
        repo.update(updated)

        result = repo.get(invoice_new.id)

        assert result.status == FinancialRecordStatus.IN_PROGRESS

    def test_invoice_repository_get_for_assignment(
            self,
            invoice_new,
            invoice_in_progress,
            invoice_processed,
    ):
        repo = InMemoryFinancialRecordRepository()

        repo.add(invoice_new)
        repo.add(invoice_in_progress)
        repo.add(invoice_processed)

        result = repo.get_for_assignment([FinancialRecordStatus.NEW_COST, FinancialRecordStatus.IN_PROGRESS])

        assert len(result) == 2
        statuses = {inv.status for inv in result}

        assert FinancialRecordStatus.NEW_COST in statuses
        assert FinancialRecordStatus.IN_PROGRESS in statuses
        assert FinancialRecordStatus.PROCESSED not in statuses



