import logging
from dataclasses import replace
from pathlib import Path

from contract_costs.infrastructure.openai_invoice_client import OpenAIInvoiceClient
from contract_costs.model.company import CompanyType
from contract_costs.repository.company_repository import CompanyRepository
from contract_costs.services.catalogues.invoice_file_organizer import InvoiceFileOrganizer
from contract_costs.services.invoices.commands.invoice_command import InvoiceCommand

from contract_costs.services.invoices.company_resolve_service import CompanyResolveService
from contract_costs.services.invoices.dto.common import InvoiceLineUpdate, ResolvedInvoiceUpdate, \
    InvoiceIngestBatch

from contract_costs.services.invoices.normalization.invoice_parser_normalizer import InvoiceParseNormalizer
from contract_costs.services.invoices.ochestrator.invoice_ingest_orchestrator import InvoiceIngestOrchestrator
from contract_costs.services.invoices.parsers.invoice_parser import InvoiceParser


logger = logging.getLogger(__name__)

class ParseInvoiceFromFileService:
    """
    Importuje fakturę z pliku (PDF / image / etc.)
    i zapisuje ją do systemu w statusie NEW.
    """

    def __init__(
        self,
        parser: InvoiceParser,
        company_resolve_service: CompanyResolveService,
        invoice_file_organizer: InvoiceFileOrganizer,
        company_repository: CompanyRepository,
        normalizer: InvoiceParseNormalizer,
        orchestrator: InvoiceIngestOrchestrator

    ) -> None:
        self._parser = parser
        self._company_resolver = company_resolve_service
        self._invoice_file_organizer = invoice_file_organizer
        self._company_repository = company_repository
        self._normalizer = normalizer
        self._orchestrator = orchestrator


    def execute(self, file_path: Path) -> None:
        """
        Główny entry-point importu faktury z pliku.
        """
        # Parsowanie dokumentu (DTO!)

        logger.info("Parsing invoice file: %s", file_path)

        parse_result = self._parser.parse(file_path)

        parse_result = self._normalizer.normalize(parse_result)

        # Resolve firm (NIP → Company.id)
        try:
            buyer_id = self._company_resolver.resolve(parse_result.buyer)
            seller_id = self._company_resolver.resolve(parse_result.seller)
        except ValueError as e:
            self._invoice_file_organizer.move_to_failed(
                file_path=file_path,
                reason="company_resolve_failed",
            )
            logger.warning(
                "Invoice skipped: company resolve failed (%s). File moved to failed.",
                str(e),
            )
            return

        buyer = self._company_repository.get(buyer_id)
        seller = self._company_repository.get(seller_id)

        ## CASE 1: faktura kosztowa (buyer = OWN) działamy:
        if buyer.role == CompanyType.OWN and buyer.is_active:
            logger.info(
                "Cost invoice detected (buyer=OWN). Invoice number=%s",
                parse_result.invoice.invoice_number,
            )

            # Uzupełnienie ResolvedInvoiceUpdate
            invoice_update: list[ResolvedInvoiceUpdate] =[
                ResolvedInvoiceUpdate(
                    command= InvoiceCommand.APPLY,

                    invoice_number=parse_result.invoice.invoice_number,
                    old_invoice_number=parse_result.invoice.old_invoice_number,

                    invoice_date=parse_result.invoice.invoice_date,
                    selling_date=parse_result.invoice.selling_date,

                    buyer_id=buyer_id,
                    seller_id=seller_id,

                    payment_method=parse_result.invoice.payment_method,
                    due_date=parse_result.invoice.due_date,
                    payment_status=parse_result.invoice.payment_status,
                    status=parse_result.invoice.status
                )
            ]

            # Jednoznaczna referencja faktury dla linii - jesli przeslemy w invoice_id nr faktury to zostanie do niej
            # automatycznie dopięte pozycje z tym smamy nipem

            invoice_ref = invoice_update[0].invoice_number

            # Uzupełnienie linii o invoice_ref
            line_updates: list[InvoiceLineUpdate] = []
            for line in parse_result.lines:
                line_updates.append(
                    replace(
                        line,
                        invoice_number=invoice_ref,
                    )
                )

            # Batch apply (faktura + linie)
            batch = InvoiceIngestBatch(
                invoices=invoice_update,
                lines=line_updates,
            )

            self._orchestrator.ingest_from_pdf(
                batch=batch,
            )

            # --- FILE ORGANIZATION (after successful persistence) ---
            logger.debug(
                "Ingesting invoice %s with %d lines",
                invoice_update[0].invoice_number,
                len(line_updates),
            )
            try:
                self._invoice_file_organizer.move_to_owner(
                    file_path=file_path,
                    owner=buyer,
                    issue_date=parse_result.invoice.invoice_date,
                    seller_name = seller.name.strip() if seller.name and seller.name.strip() else "FAKTURA",
                    invoice_number = invoice_ref
                )
            except Exception:
                logger.exception(
                    "Invoice imported but file move failed: %s",
                    invoice_update[0].invoice_number,
                )
            logger.info(
                "Invoice %s successfully imported and file moved to owner folder",
                invoice_update[0].invoice_number,
            )
            return

        # CASE 2: faktura przychodowa (seller = OWN) – na razie nieobsługiwana - tylko przenosimy fakturę
        if seller.role == CompanyType.OWN and seller.is_active:
            self._invoice_file_organizer.move_to_failed(
                file_path=file_path,
                reason="revenue_not_supported",
            )
            logger.warning(
                "Revenue invoice detected (seller=OWN). File moved to failed.",
            )
            return

        # CASE 3: obca / błędna faktura, faktura nie posiada w żadnego klienta OWN company
        self._invoice_file_organizer.move_to_failed(
            file_path=file_path,
            reason="no_owner",
        )
        logger.warning(
            "Invoice skipped: no OWN company found. File moved to failed."
        )