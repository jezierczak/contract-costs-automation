# import logging
# from dataclasses import replace
# from pathlib import Path
# from uuid import UUID
#
# from contract_costs.model.company import CompanyType
# from contract_costs.model.financial_record import FinancialRecord, FinancialRecordStatus
# from contract_costs.repository.company_repository import CompanyRepository
# from contract_costs.repository.financial_record_repository import FinancialRecordRepository
# from contract_costs.services.catalogues.invoice_file_organizer import RecordFileOrganizer
# import contract_costs.config as cfg
#
# logger = logging.getLogger(__name__)
#
#
# class InvoiceFileWorkflowService:
#     """
#       Odpowiada WYŁĄCZNIE za:
#       - synchronizację położenia pliku faktury
#       - na podstawie aktualnego stanu FinancialRecord
#       - w obrębie sandboxa organizacji
#       """
#
#     def __init__(
#         self,
#         record_repository: FinancialRecordRepository,
#         company_repository: CompanyRepository,
#         file_organizer: RecordFileOrganizer,
#     ) -> None:
#         self._record_repository = record_repository
#         self._company_repository = company_repository
#         self._file_organizer = file_organizer
#
#     def sync(
#             self,
#             *,
#             organization_id: UUID,
#             record: FinancialRecord,
#     ) -> None:
#
#         if not record.scan_filename:
#             logger.debug(
#                 "Invoice %s has no scan file, skipping file workflow",
#                 record.id,
#             )
#             return
#
#         org_root = cfg.WORK_DIR / str(organization_id)
#
#         current_relative = Path(record.scan_filename)
#         current_path = org_root  / current_relative
#
#         if not current_path.exists():
#             logger.warning(
#                 "Scan file does not exist for record  %s: %s",
#                 record.id,
#                 current_path,
#             )
#             return
#
#
#         buyer = (
#             self._company_repository.get(
#                 organization_id=organization_id,
#                 company_id=record.buyer_id,
#             )
#             if record.buyer_id else None
#         )
#         seller = (
#             self._company_repository.get(
#                 organization_id=organization_id,
#                 company_id=record.seller_id,
#             )
#             if record.seller_id else None
#         )
#
#         if not buyer or not seller:
#             target_relative = self._file_organizer.move_to_draft(
#                 root=org_root,
#                 file_path=current_path,
#             )
#
#         elif record.status == FinancialRecordStatus.DELETED:
#             target_relative = self._file_organizer.move_to_trash(
#                 root=org_root,
#                 file_path=current_path,
#             )
#
#
#         elif buyer.role == CompanyType.OWN:
#             target_relative = self._file_organizer.move_to_owner(
#                 root=org_root,
#                 file_path=current_path,
#                 kind="cost",
#                 owner=buyer,
#                 issue_date=record.invoice_date,
#                 client_name=seller.name,
#                 record_ref_number=record.reference,
#             )
#
#         elif seller.role == CompanyType.OWN:
#             target_relative = self._file_organizer.move_to_owner(
#                 root=org_root,
#                 file_path=current_path,
#                 kind="revenue",
#                 owner=seller,
#                 issue_date=record.invoice_date,
#                 client_name=buyer.name,
#                 record_ref_number=record.reference,
#             )
#
#         else:
#             target_relative = self._file_organizer.move_to_draft(
#                 root=org_root,
#                 file_path=current_path)
#
#         # NO CHANGE
#         if target_relative.as_posix() == record.scan_filename:
#             logger.debug(
#                 "Record %s file unchanged: %s",
#                 record.id,
#                 current_relative,
#             )
#             return
#
#         updated = replace(
#             record,
#             scan_filename=target_relative.as_posix(),
#         )
#         self._record_repository.update(updated)
#
#         logger.info(
#             "Invoice %s file moved: %s → %s",
#             record.id,
#             current_path,
#             org_root / target_relative,
#         )
#
