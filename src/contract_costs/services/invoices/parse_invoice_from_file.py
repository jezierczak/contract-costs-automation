from dataclasses import replace
from pathlib import Path

from contract_costs.model.company import CompanyType
from contract_costs.model.invoice import InvoiceStatus
from contract_costs.repository.company_repository import CompanyRepository
from contract_costs.services.catalogues.invoice_file_organizer import InvoiceFileOrganizer

from contract_costs.services.invoices.company_resolve_service import CompanyResolveService
from contract_costs.services.invoices.dto.common import InvoiceLineUpdate, InvoiceExcelBatch
from contract_costs.services.invoices.invoice_line_update_service import InvoiceLineUpdateService
from contract_costs.services.invoices.invoice_update_service import InvoiceUpdateService
from contract_costs.services.invoices.parsers.invoice_parser import InvoiceParser


class ParseInvoiceFromFileService:
    """
    Importuje fakturę z pliku (PDF / image / etc.)
    i zapisuje ją do systemu w statusie NEW.
    """

    def __init__(
        self,
        parser: InvoiceParser,
        company_resolve_service: CompanyResolveService,
        invoice_update_service: InvoiceUpdateService,
        invoice_line_update_service: InvoiceLineUpdateService,
        invoice_file_organizer: InvoiceFileOrganizer,
        company_repository: CompanyRepository,
    ) -> None:
        self._parser = parser
        self._company_resolver = company_resolve_service
        self._invoice_update_service = invoice_update_service
        self._invoice_line_update_service = invoice_line_update_service
        self._invoice_file_organizer = invoice_file_organizer
        self._company_repository = company_repository

    def execute(self, file_path: Path) -> None:
        """
        Główny entry-point importu faktury z pliku.
        """
        # Parsowanie dokumentu (DTO!)
        parse_result = self._parser.parse(file_path)

        # Resolve firm (NIP → Company.id)
        buyer_id = self._company_resolver.resolve(parse_result.buyer)
        seller_id = self._company_resolver.resolve(parse_result.seller)

        # Uzupełnienie InvoiceUpdate
        invoice_update = replace(
            parse_result.invoice,
            buyer_id=buyer_id,
            seller_id=seller_id,
            status=InvoiceStatus.NEW,
        )

        # Jednoznaczna referencja faktury dla linii
        # (parser zwykle generuje external_ref)
        invoice_ref = invoice_update.ref

        # Uzupełnienie linii o invoice_ref
        line_updates: list[InvoiceLineUpdate] = []
        for line in parse_result.lines:
            line_updates.append(
                replace(
                    line,
                    invoice_ref=invoice_ref,
                )
            )

        # Batch apply (faktura + linie)
        batch = InvoiceExcelBatch(
            invoices=[invoice_update],
            lines=line_updates,
        )

        ref_map = self._invoice_update_service.apply(batch.invoices)
        self._invoice_line_update_service.apply(batch.lines, ref_map)

        # --- FILE ORGANIZATION (after successful persistence) ---

        buyer = self._company_repository.get(buyer_id)
        seller = self._company_repository.get(seller_id)

        # CASE 1: faktura kosztowa (buyer = OWN)
        if buyer.role == CompanyType.OWN and buyer.is_active:
            self._invoice_file_organizer.move_to_owner(
                file_path=file_path,
                owner=buyer,
                issue_date=parse_result.invoice.invoice_date,
            )
            return

        # CASE 2: faktura przychodowa (seller = OWN) – na razie nieobsługiwana
        if seller.role == CompanyType.OWN and seller.is_active:
            self._invoice_file_organizer.move_to_failed(
                file_path=file_path,
                reason="revenue_not_supported",
            )
            return

        # CASE 3: obca / błędna faktura
        self._invoice_file_organizer.move_to_failed(
            file_path=file_path,
            reason="no_owner",
        )