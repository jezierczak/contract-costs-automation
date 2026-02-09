# import logging
# from dataclasses import replace
# from pathlib import Path
# from uuid import UUID
#
# from contract_costs.model.company import CompanyType
# from contract_costs.model.financial_record import FinancialRecordStatus
# from contract_costs.services.catalogues.invoice_file_organizer import RecordFileOrganizer
# from contract_costs.services.companies.company_evaluate_orchestrator import CompanyEvaluateOrchestrator
# from contract_costs.services.financial_records.assigment.apply.commands.invoice_command import InvoiceCommand
#
#
# from contract_costs.services.financial_records.assigment.invoice_sources.dto.common import ResolvedFinancialRecordUpdate, \
#     RecordIngestBatch
#
# from contract_costs.services.financial_records.assigment.invoice_sources.normalization.invoice_parser_normalizer import DocumentParseNormalizer
# from contract_costs.services.financial_records.assigment.ingest.financial_record_ingest_orchestrator import FinancialRecordIngestOrchestrator
# from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.document_parser import DocumentParser
#
# import contract_costs.config as cfg
#
#
# logger = logging.getLogger(__name__)
#
# class ParseInvoiceFromFileService:
#     """
#     PDF ingest:
#     - zapisuje plik do RAW
#     - rejestruje fakturę (NEW / DRAFT)
#     - NIE decyduje o cost / revenue
#     """
#
#     def __init__(
#         self,
#         parser: DocumentParser,
#         company_evaluate_orchestrator: CompanyEvaluateOrchestrator,
#         record_file_organizer: RecordFileOrganizer,
#         normalizer: DocumentParseNormalizer,
#         orchestrator: FinancialRecordIngestOrchestrator,
#     ) -> None:
#         self._parser = parser
#         self._company_evaluate_orchestrator = company_evaluate_orchestrator
#         self._record_file_organizer = record_file_organizer
#         self._normalizer = normalizer
#         self._orchestrator = orchestrator
#
#     def execute(self,
#                 *,
#                 organization_id: UUID,
#                 actor_user_id: UUID,
#                 file_path: Path) -> None:
#         logger.info("Parsing invoice file: %s", file_path)
#
#         # 1️⃣ PARSE + NORMALIZE
#         parse_result = self._normalizer.normalize(
#             self._parser.parse(file_path)
#         )
#
#         buyer = self._company_evaluate_orchestrator.evaluate(
#             organization_id=organization_id,
#             actor_user_id=actor_user_id,
#             input_=parse_result.buyer)
#         seller = self._company_evaluate_orchestrator.evaluate(
#             organization_id=organization_id,
#             actor_user_id=actor_user_id,
#             input_=parse_result.seller)
#
#         # 2️⃣ MOVE FILE → RAW (ZAWSZE)
#         try:
#             org_root = cfg.WORK_DIR / str(organization_id)
#             raw_path = self._record_file_organizer.move_to_raw(root=org_root,file_path=file_path)
#         except Exception:
#             logger.exception("Failed to move file to RAW, aborting ingest")
#             return
#
#         # 3️⃣ STATUS (TYLKO WSTĘPNY)
#         if buyer.role == CompanyType.OWN and buyer.is_active:
#             status = FinancialRecordStatus.NEW_COST
#
#         elif seller.role == CompanyType.OWN and seller.is_active:
#             status = FinancialRecordStatus.NEW_REVENUE  # ⬅️ TU STOP
#
#         else:
#             status = FinancialRecordStatus.DRAFT
#
#         # 4️⃣ BUILD UPDATE
#         record_update = [
#             ResolvedFinancialRecordUpdate(
#                 command=InvoiceCommand.APPLY,
#                 reference=parse_result.record.reference,
#                 record_id= None,
#                 old_record_reference=parse_result.record.old_reference,
#                 invoice_date=parse_result.record.invoice_date,
#                 selling_date=parse_result.record.selling_date,
#                 buyer=buyer,
#                 seller=seller,
#                 payment_method=parse_result.record.payment_method,
#                 due_date=parse_result.record.due_date,
#                 paid_date=parse_result.record.paid_date,
#                 payment_status=parse_result.record.payment_status,
#                 status=status,
#                 scan_filename=raw_path.as_posix(),
#                 tags=None,
#             )
#         ]
#
#         line_updates = [
#             replace(line, record_reference=parse_result.record.reference)
#             for line in parse_result.lines
#         ]
#
#         batch = RecordIngestBatch(
#             financial_records=record_update,
#             lines=line_updates,
#         )
#
#         # 5️⃣ INGEST (PDF)
#         self._orchestrator.ingest_from_document(
#             organization_id=organization_id, actor_user_id=actor_user_id, batch=batch)
#
#
#         logger.info(
#             "PDF invoice registered: %s (status=%s, raw=%s)",
#             parse_result.record.reference,
#             status,
#             raw_path,
#         )
