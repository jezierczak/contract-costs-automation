import logging
from dataclasses import replace
from datetime import datetime
from pathlib import Path

from contract_costs.model.company import CompanyType, Company
from contract_costs.model.invoice import InvoiceStatus
from contract_costs.repository.company_repository import CompanyRepository
from contract_costs.services.catalogues.invoice_file_organizer import InvoiceFileOrganizer
from contract_costs.services.companies.company_evaluate_orchestrator import CompanyEvaluateOrchestrator
from contract_costs.services.invoices.assigment.apply.commands.invoice_command import InvoiceCommand


from contract_costs.services.invoices.assigment.invoice_sources.dto.common import InvoiceLineUpdate, ResolvedInvoiceUpdate, \
    InvoiceIngestBatch

from contract_costs.services.invoices.assigment.invoice_sources.normalization.invoice_parser_normalizer import InvoiceParseNormalizer
from contract_costs.services.invoices.assigment.ingest.invoice_ingest_orchestrator import InvoiceIngestOrchestrator
from contract_costs.services.invoices.assigment.invoice_sources.pdf.parsers.dto.parse import InvoiceParseResult
from contract_costs.services.invoices.assigment.invoice_sources.pdf.parsers.invoice_parser import InvoiceParser


logger = logging.getLogger(__name__)

class ParseInvoiceFromFileService:
    """
    PDF ingest:
    - zapisuje plik do RAW
    - rejestruje fakturę (NEW / DRAFT)
    - NIE decyduje o cost / revenue
    """

    def __init__(
        self,
        parser: InvoiceParser,
        company_evaluate_orchestrator: CompanyEvaluateOrchestrator,
        invoice_file_organizer: InvoiceFileOrganizer,
        normalizer: InvoiceParseNormalizer,
        orchestrator: InvoiceIngestOrchestrator,
    ) -> None:
        self._parser = parser
        self._company_evaluate_orchestrator = company_evaluate_orchestrator
        self._invoice_file_organizer = invoice_file_organizer
        self._normalizer = normalizer
        self._orchestrator = orchestrator

    def execute(self, file_path: Path) -> None:
        logger.info("Parsing invoice file: %s", file_path)

        # 1️⃣ PARSE + NORMALIZE
        parse_result = self._normalizer.normalize(
            self._parser.parse(file_path)
        )

        buyer = self._company_evaluate_orchestrator.evaluate(parse_result.buyer)
        seller = self._company_evaluate_orchestrator.evaluate(parse_result.seller)

        # 2️⃣ MOVE FILE → RAW (ZAWSZE)
        try:
            raw_path = self._invoice_file_organizer.move_to_raw(file_path)
        except Exception:
            logger.exception("Failed to move file to RAW, aborting ingest")
            return

        # 3️⃣ STATUS (TYLKO WSTĘPNY)
        if buyer.role == CompanyType.OWN and buyer.is_active:
            status = InvoiceStatus.NEW_COST

        elif seller.role == CompanyType.OWN and seller.is_active:
            status = InvoiceStatus.NEW_REVENUE  # ⬅️ TU STOP

        else:
            status = InvoiceStatus.DRAFT

        # 4️⃣ BUILD UPDATE
        invoice_update = [
            ResolvedInvoiceUpdate(
                command=InvoiceCommand.APPLY,
                invoice_number=parse_result.invoice.invoice_number,
                invoice_id = None,
                old_invoice_number=parse_result.invoice.old_invoice_number,
                invoice_date=parse_result.invoice.invoice_date,
                selling_date=parse_result.invoice.selling_date,
                buyer=buyer,
                seller=seller,
                payment_method=parse_result.invoice.payment_method,
                due_date=parse_result.invoice.due_date,
                paid_date=parse_result.invoice.paid_date,
                payment_status=parse_result.invoice.payment_status,
                status=status,
                scan_filename=raw_path.as_posix(),
                tags=None,
            )
        ]

        line_updates = [
            replace(line, invoice_number=parse_result.invoice.invoice_number)
            for line in parse_result.lines
        ]

        batch = InvoiceIngestBatch(
            invoices=invoice_update,
            lines=line_updates,
        )

        # 5️⃣ INGEST (PDF)
        self._orchestrator.ingest_from_pdf(batch)

        logger.info(
            "PDF invoice registered: %s (status=%s, raw=%s)",
            parse_result.invoice.invoice_number,
            status,
            raw_path,
        )
