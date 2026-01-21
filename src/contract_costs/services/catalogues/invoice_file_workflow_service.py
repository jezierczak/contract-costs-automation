import logging
from dataclasses import replace
from pathlib import Path

from contract_costs.model.company import CompanyType
from contract_costs.model.invoice import Invoice, InvoiceStatus
from contract_costs.repository.company_repository import CompanyRepository
from contract_costs.repository.invoice_repository import InvoiceRepository
from contract_costs.services.catalogues.invoice_file_organizer import InvoiceFileOrganizer
import contract_costs.config as cfg

logger = logging.getLogger(__name__)


class InvoiceFileWorkflowService:
    """
    Odpowiada WYŁĄCZNIE za:
    - synchronizację położenia pliku faktury
    - na podstawie aktualnego stanu Invoice
    """

    def __init__(
        self,
        invoice_repository: InvoiceRepository,
        company_repository: CompanyRepository,
        file_organizer: InvoiceFileOrganizer,
    ) -> None:
        self._invoice_repository = invoice_repository
        self._company_repository = company_repository
        self._file_organizer = file_organizer

    def sync(self, invoice: Invoice) -> None:
        if not invoice.scan_filename:
            logger.debug(
                "Invoice %s has no scan file, skipping file workflow",
                invoice.id,
            )
            return

        current_relative = Path(invoice.scan_filename)
        current_path = cfg.WORK_DIR / current_relative

        if not current_path.exists():
            logger.warning(
                "Scan file does not exist for invoice %s: %s",
                invoice.id,
                current_path,
            )
            return

        buyer = self._company_repository.get(invoice.buyer_id)
        seller = self._company_repository.get(invoice.seller_id)

        if not buyer or not seller:
            target_relative = self._file_organizer.move_to_draft(current_path)

        elif invoice.status == InvoiceStatus.DELETED:
            target_relative = self._file_organizer.move_to_trash(current_path)

        elif buyer.role == CompanyType.OWN:
            target_relative = self._file_organizer.move_to_owner(
                file_path=current_path,
                kind="cost",
                owner=buyer,
                issue_date=invoice.invoice_date,
                client_name=seller.name,
                invoice_number=invoice.invoice_number,
            )

        elif seller.role == CompanyType.OWN:
            target_relative = self._file_organizer.move_to_owner(
                file_path=current_path,
                kind="revenue",
                owner=seller,
                issue_date=invoice.invoice_date,
                client_name=buyer.name,
                invoice_number=invoice.invoice_number,
            )

        else:
            target_relative = self._file_organizer.move_to_draft(current_path)

        # NO CHANGE
        if target_relative.as_posix() == invoice.scan_filename:
            logger.debug(
                "Invoice %s file unchanged: %s",
                invoice.id,
                current_relative,
            )
            return

        updated = replace(
            invoice,
            scan_filename=target_relative.as_posix(),
        )
        self._invoice_repository.update(updated)

        logger.info(
            "Invoice %s file moved: %s → %s",
            invoice.id,
            current_path,
            cfg.WORK_DIR / target_relative,
        )

