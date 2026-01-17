import logging
from dataclasses import replace
from datetime import datetime
from pathlib import Path

from contract_costs.model.company import CompanyType
from contract_costs.repository.company_repository import CompanyRepository
from contract_costs.services.catalogues.invoice_file_organizer import InvoiceFileOrganizer
from contract_costs.services.companies.company_evaluate_orchestrator import CompanyEvaluateOrchestrator
from contract_costs.services.invoices.assigment.apply.commands.invoice_command import InvoiceCommand


from contract_costs.services.invoices.assigment.invoice_sources.dto.common import InvoiceLineUpdate, ResolvedInvoiceUpdate, \
    InvoiceIngestBatch

from contract_costs.services.invoices.assigment.invoice_sources.normalization.invoice_parser_normalizer import InvoiceParseNormalizer
from contract_costs.services.invoices.assigment.ingest.invoice_ingest_orchestrator import InvoiceIngestOrchestrator
from contract_costs.services.invoices.assigment.invoice_sources.pdf.parsers.invoice_parser import InvoiceParser


logger = logging.getLogger(__name__)

class ParseInvoiceFromFileService:
    """
    Importuje fakturę z pliku (PDF / image / etc.)
    i zapisuje ją do systemu w statusie NEW.
    """

    def __init__(
        self,
        parser: InvoiceParser,
        company_evaluate_orchestrator: CompanyEvaluateOrchestrator,
        invoice_file_organizer: InvoiceFileOrganizer,
        company_repository: CompanyRepository,
        normalizer: InvoiceParseNormalizer,
        orchestrator: InvoiceIngestOrchestrator

    ) -> None:
        self._parser = parser
        self._company_evaluate_orchestrator = company_evaluate_orchestrator
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

        buyer= self._company_evaluate_orchestrator.evaluate(parse_result.buyer)
        seller = self._company_evaluate_orchestrator.evaluate(parse_result.seller)

        # ============================================================
        # CASE 1: COST INVOICE (buyer = OWN)
        # ============================================================
        if buyer.role == CompanyType.OWN and buyer.is_active:
            invoice_number = parse_result.invoice.invoice_number

            logger.info(
                "Cost invoice detected (buyer=OWN). Invoice number=%s",
                invoice_number,
            )

            # --- MOVE FILE FIRST (SOURCE OF TRUTH) ---
            try:
                relative_path = self._invoice_file_organizer.move_to_owner(
                    file_path=file_path,
                    owner=buyer,
                    issue_date=(
                        parse_result.invoice.invoice_date
                        if parse_result.invoice.invoice_date
                        else datetime.now().date()
                    ),
                    seller_name=seller.name.strip()
                    if seller.name and seller.name.strip()
                    else "FAKTURA",
                    invoice_number=invoice_number or "UNKNOWN_INVOICE_NUMBER",
                )
            except Exception:
                logger.exception(
                    "File move failed, invoice will NOT be ingested: %s",
                    invoice_number,
                )
                return

            # --- BUILD INVOICE UPDATE (AFTER MOVE) ---
            invoice_update = [
                ResolvedInvoiceUpdate(
                    command=InvoiceCommand.APPLY,

                    invoice_number=invoice_number,
                    old_invoice_number=parse_result.invoice.old_invoice_number,

                    invoice_date=parse_result.invoice.invoice_date,
                    selling_date=parse_result.invoice.selling_date,

                    buyer_id=buyer.id,
                    seller_id=seller.id,

                    payment_method=parse_result.invoice.payment_method,
                    due_date=parse_result.invoice.due_date,
                    paid_date=parse_result.invoice.paid_date,
                    payment_status=parse_result.invoice.payment_status,
                    status=parse_result.invoice.status,

                    scan_filename=relative_path.as_posix(),
                    tags=None,
                )
            ]

            invoice_ref = invoice_number

            # --- LINE UPDATES ---
            line_updates: list[InvoiceLineUpdate] = [
                replace(line, invoice_number=invoice_ref)
                for line in parse_result.lines
            ]

            batch = InvoiceIngestBatch(
                invoices=invoice_update,
                lines=line_updates,
            )

            # --- INGEST ---
            self._orchestrator.ingest_from_pdf(batch=batch)

            logger.info(
                "Invoice %s successfully imported. File stored at %s",
                invoice_number,
                relative_path,
            )
            return

        # ============================================================
        # CASE 2: REVENUE INVOICE (seller = OWN) – not supported yet
        # ============================================================
        if seller.role == CompanyType.OWN and seller.is_active:
            self._invoice_file_organizer.move_to_failed(
                file_path=file_path,
                reason="revenue_not_supported",
            )
            logger.warning(
                "Revenue invoice detected (seller=OWN). File moved to failed."
            )
            return

        # ============================================================
        # CASE 3: NO OWN COMPANY
        # ============================================================
        self._invoice_file_organizer.move_to_failed(
            file_path=file_path,
            reason="no_owner",
        )
        logger.warning(
            "Invoice skipped: no OWN company found. File moved to failed."
        )