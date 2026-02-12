
from contract_costs.action_bus.permission_resolver import  MySqlPermissionResolver
from contract_costs.services.contracts.apply.apply_contract_progress_service import ApplyContractProgressService

from contract_costs.services.contracts.builders.contract_node_tree_builder import DefaultContractNodeTreeBuilder
from contract_costs.common.context.context_provider import ContextProvider
from contract_costs.common.context.file_context_provider import FileContextProvider
from contract_costs.infrastructure.excel.base_excel_exporter import BaseExcelExporter
from contract_costs.infrastructure.excel.invoice_action_excel_loader import FinancialRecordActionExcelLoader
from contract_costs.services.catalogues.document_file_organizer import DocumentFileOrganizer
from contract_costs.services.catalogues.record_file_organizer import RecordFileOrganizer
from contract_costs.services.catalogues.record_file_workworkflow_service import RecordFileWorkflowService
from contract_costs.services.companies.activate_company_service import ActivateCompanyService
from contract_costs.services.companies.apply.apply_companies_from_excel_service import ApplyCompaniesFromExcelService
from contract_costs.services.companies.company_evaluate_orchestrator import CompanyEvaluateOrchestrator
from contract_costs.services.companies.deactivate_company_service import DeactivateCompanyService
from contract_costs.services.companies.providers.street import StreetCandidateProvider
from contract_costs.services.companies.providers.bank import BankAccountCandidateProvider
from contract_costs.services.companies.providers.composite import CompositeCompanyCandidateProvider
from contract_costs.services.companies.providers.email import EmailCandidateProvider
from contract_costs.services.companies.providers.excact_nip import ExactNipCandidateProvider
from contract_costs.services.companies.create_company_service import CreateCompanyService
from contract_costs.services.companies.providers.name import NameCandidateProvider
from contract_costs.services.companies.providers.phone import PhoneCandidateProvider
from contract_costs.services.companies.query.company_query_service import CompanyQueryService
from contract_costs.services.companies.update_company_service import UpdateCompanyService
from contract_costs.services.contracts.apply.apply_contract_progress_excel_service import \
    ApplyContractProgressExcelService
from contract_costs.services.contracts.apply.set_contract_status_service import SetContractStatusService
from contract_costs.services.contracts.create_contract_service import CreateContractService
from contract_costs.services.contracts.migration.back_fill_system_contracts_service import \
    BackfillSystemContractsService

from contract_costs.services.contracts.prepare.contract_prepare_excel_exporter import ContractPrepareExcelExporter
from contract_costs.services.contracts.prepare.contract_prepare_progress_excel_exporter import \
    ContractPrepareProgressExcelExporter
from contract_costs.services.contracts.query.contract_details.contract_details_query_service import \
    ContractDetailsQueryService
from contract_costs.services.contracts.query.contract_query_service import ContractQueryService

from contract_costs.services.contracts.apply.update_contract_structure_service import (
    UpdateContractStructureService,
)
from contract_costs.services.contracts.apply.apply_contract_structure_excel import (
    ApplyContractStructureExcelService,
)
from contract_costs.services.contracts.query.list_contracts.list_contracts_query_service import \
    ListContractsQueryService
from contract_costs.services.contracts.system_contract.create_system_contract_orchestrator import \
    CreateSystemContractOrchestrator

from contract_costs.services.contracts.validators.contract_node_tree_validator import (
    ContractNodeEntityValidator,
)
from contract_costs.services.documents.apply.apply_document_service import ApplyDocumentService
from contract_costs.services.documents.apply.document_action_excel_loader import DocumentActionExcelLoader
from contract_costs.services.documents.migrate_scan_filename_service import MigrateScanFilenameService
from contract_costs.services.documents.process.delete.delete_command_service import DeleteDocumentService
from contract_costs.services.documents.process.document_parser_resolver import DefaultDocumentParserResolver
from contract_costs.services.documents.process.parse_document_from_file import ParseDocumentFromFileService
from contract_costs.services.documents.process.reprocess.reprocess_document_service import ReprocessDocumentService
from contract_costs.services.documents.query.list_documents_query_service import ListDocumentsQueryService
from contract_costs.services.financial_records.assigment.invoice_sources.document.create_record_from_document_service import \
    CreateRecordFromDocumentService

from contract_costs.services.identity.add.add_organization_user_service import AddOrganizationUserService
from contract_costs.services.identity.add.create_organization_with_owner import CreateOrganizationWithOwnerService
from contract_costs.services.identity.add.create_user_service import CreateUserService
from contract_costs.services.identity.query.show_organization_users import ShowOrganizationUsersQueryService
from contract_costs.services.identity.query.show_organizations import ShowOrganizationsQueryService
from contract_costs.services.identity.remove.remove_organization_user_service import RemoveOrganizationUserService
from contract_costs.services.identity.use.use_organization_service import UseOrganizationService
from contract_costs.services.financial_records.assigment.ingest.completion_validator.invoice_completion_validator import RecordCompletionValidator
from contract_costs.services.number_generator.number_generator import NumberGenerator
from contract_costs.services.snapshots.contract_snapshot_query_service import ContractSnapshotQueryService
from contract_costs.services.snapshots.create_contract_snapshot_service import CreateContractSnapshotService
from contract_costs.services.value_types.apply.change_value_type_code_service import ChangeValueTypeCodeService
from contract_costs.services.value_types.apply.deactivate_value_type_service import DeactivateValueTypeService
from contract_costs.services.value_types.apply.update_value_type_service import UpdateValueTypeService
from contract_costs.services.value_types.create_value_type_service import CreateValueTypeService
from contract_costs.services.value_types.query.value_type_query_service import ValueTypeQueryService
from contract_costs.services.financial_records.actions.financial_record_action_service import FinancialRecordActionService
from contract_costs.services.financial_records.assigment.ingest.excel_financial_record_ingest_service import ExcelFinancialRecordIngestService
from contract_costs.services.financial_records.assigment.ingest.pdf_financial_record_ingest_service import PdfFinancialRecordIngestService

from contract_costs.services.financial_records.assigment.invoice_sources.excel.invoice_excel_resolver import FinancialRecordExcelBatchResolver
from contract_costs.services.financial_records.assigment.invoice_sources.normalization.invoice_parser_normalizer import \
    DocumentParseNormalizer
from contract_costs.services.financial_records.assigment.prepare.export.export_invoice_assignment_excel_service import \
    ExportFinancialRecordAssignmentExcelService
from contract_costs.services.financial_records.excel.invoice_excel_export_service import FinancialRecordExcelExportService
from contract_costs.services.financial_records.queries.financial_record_details_query_service import FinancialRecordDetailsQueryService
from contract_costs.services.financial_records.assigment.ingest.financial_record_line_update_service import FinancialRecordLineUpdateService
from contract_costs.services.financial_records.assigment.ingest.financial_record_ingest_orchestrator import (
    FinancialRecordIngestOrchestrator,
)


from contract_costs.services.financial_records.assigment.apply.apply_financial_record_excel_batch_service import (
    ApplyFinancialRecordExcelBatchService,
)
from contract_costs.services.financial_records.assigment.apply.apply_company_excel_batch_service import (
    ApplyCompanyExcelBatchService,
)
from contract_costs.services.financial_records.assigment.prepare.generate_assignment_bundle_service import (
    GenerateFinancialRecordAssignmentBundleService,
)
from contract_costs.services.financial_records.assigment.prepare.export.excel_invoice_assignment_exporter import \
    ExcelInvoiceAssignmentExporter

from contract_costs.repository.factory.repository_factory import (
    RepositoryFactory,
    RepoBackend,
)
from typing import Dict

from contract_costs.services.financial_records.review.financial_record_review_list_query_service import FinancialRecordReviewListQueryService
from contract_costs.services.workers.document_parse_worker import DocumentParseWorker


class Services:
    def __init__(self,
                 backend: RepoBackend = RepoBackend.MYSQL,
                 context_provider: ContextProvider | None = None,

                ) -> None:
        self._factory = RepositoryFactory(backend)
        if context_provider is None:
            raise RuntimeError("ContextProvider must be provided")
        self._context = context_provider

        self._action_bus = None
        self._permission_validator = None
        self._service_registry = None

        # repos
        self._company_repo = None
        self._record_repo = None
        self._record_line_repo = None
        self._contract_repo = None
        self._contract_node_repo = None
        self._value_type_repo = None
        self._contract_snapshot_repo = None
        self._contract_node_snapshot_repo = None
        self._contract_node_value_snapshot_repo = None
        self._organization_repo = None
        self._organization_user_repo = None
        self._user_repo = None
        self._document_repo = None
        self._number_sequence_repo = None

        # services
        # self._company_resolver = None
        self._financial_record_ingest_orchestrator = None
        # self._parse_invoice_from_file = None
        self._apply_financial_record_excel_batch = None
        self._invoice_watcher_service = None
        self._generate_financial_record_assignment_bundle=None
        self._export_financial_record_assignment_excel = None
        self._create_company_service = None
        self._update_company_service = None
        self._create_value_type = None
        self._create_contract = None
        # self._update_contract_service = None
        self._update_contract_structure_service = None
        self._apply_contract_structure_excel = None
        self._generate_contract_structure_bundle = None
        self._export_contract_structure_excel = None

        self._document_parse_worker = None

        self._contract_cost_report =None
        self._open_ai_invoice_service = None
        self._company_evaluate_orchestrator =None

        self._financial_record_query_service = None

        # self._invoice_seller_summary_query_service = None

        self._contract_query_service = None

        self._financial_record_excel_export_service = None

        self._financial_record_action_service = None
        self._financial_record_action_excel_loader = None
        self._review_query_service = None
        self._apply_companies_from_excel_service = None

        self._company_query_service = None

        self._activate_company_service = None
        self._deactivate_company_service = None
        self._value_type_query_service = None
        self._deactivate_value_type_service = None
        self._update_value_type_service = None
        self._change_value_type_code_service = None
        self._contract_prepare_excel_exporter =None
        self._set_contract_status_service = None
        self._contract_prepare_progress_excel_exporter = None
        self._apply_contract_progress_excel = None
        self._create_contract_snapshot = None
        self._contract_snapshot_query_service = None

        self._create_organization_with_owner =None
        self._show_organizations = None
        self._show_organization_users = None
        self._add_organization_user = None
        self._create_user = None
        self._remove_organization_user = None
        self._change_organization_user_role = None
        self._deactivate_organization_user = None
        self._accept_organization_invite = None
        self._upload_document_service = None
        self._process_document_service = None
        self._document_parser_resolver = None
        self._parse_document_from_file = None
        self._export_document_assignment_excel_service = None
        self._prepare_documents_service = None
        self._apply_document_service = None
        self._record_file_workflow_service = None
        self._create_record_service = None
        self._permission_resolver = None
        self._apply_contract_progress_service = None
        self._list_contracts_service = None
        self._contract_details_service = None
        self._list_documents_query_service = None
        self._reprocess_document_service = None
        self._delete_document_service = None
        self._create_system_contract = None

        self._document_action_excel_loader_service = None

        self._normalizer = DocumentParseNormalizer()

    # ---------- repositories ----------
    @property
    def permission_resolver(self):
        if self._permission_resolver is None:
            self._permission_resolver = MySqlPermissionResolver(
                org_user_repo= self.organization_user_repository
            )
        return self._permission_resolver

    @property
    def permission_validator(self):
        if self._permission_validator is None:
            from contract_costs.action_bus.permission_validator import (
                PermissionValidator,
            )

            self._permission_validator = PermissionValidator(
                permission_resolver=self.permission_resolver,
            )

        return self._permission_validator


    # @property
    # def service_registry(self):
    #     if self._service_registry is None:
    #
    #         from contract_costs.services.documents.upload.dto.upload_document_command import (
    #             UploadDocumentCommand,
    #         )
    #
    #         from contract_costs.services.documents.process.dto.process_document_command import (
    #             ProcessDocumentCommand,
    #         )
    #
    #         registry = {
    #             CreateCompanyCommand: self.create_company,
    #             UploadDocumentCommand: self.upload_document_service,
    #             ProcessDocumentCommand: self.process_document_service,
    #         }
    #         # registry = {}
    #         #
    #         # for attr_name in dir(self):
    #         #     service = getattr(self, attr_name)
    #         #
    #         #     command_type = getattr(service.__class__, "__command_type__", None)
    #         #     if command_type:
    #         #         registry[command_type] = service
    #
    #         # 🔥 UploadDocument
    #
    #         # 👉 później kolejne komendy tutaj
    #
    #         self._service_registry = registry
    #
    #     return self._service_registry

    # def _resolve_by_type(self, annotation):
    #     for attr_name in dir(self):
    #         if attr_name.startswith("_"):
    #             continue
    #
    #         try:
    #             attr = getattr(self, attr_name)
    #         except Exception:
    #             continue
    #
    #         try:
    #             if isinstance(attr, annotation):
    #                 return attr
    #         except TypeError:
    #             # np. annotation to typing stuff
    #             continue
    #
    #     return None

    @property
    def action_bus(self):
        if self._action_bus is None:
            from contract_costs.action_bus.action_bus import ActionBus
            # from contract_costs.action_bus.bootstrap import (
            #     build_handler_instances,
            # )
            #
            # import inspect
            #
            # def handler_factory(handler_cls):
            #     sig = inspect.signature(handler_cls.__init__)
            #     kwargs = {}
            #
            #     for name, param in sig.parameters.items():
            #         if name == "self":
            #             continue
            #
            #         annotation = param.annotation
            #
            #         # -------------------------------------------------
            #         # 1️⃣ TYPE-BASED RESOLUTION
            #         # -------------------------------------------------
            #         if annotation is not inspect.Parameter.empty:
            #             resolved = self._resolve_by_type(annotation)
            #             if resolved is not None:
            #                 kwargs[name] = resolved
            #                 continue
            #
            #         # -------------------------------------------------
            #         # 2️⃣ NAME-BASED FALLBACK
            #         # -------------------------------------------------
            #         if hasattr(self, name):
            #             kwargs[name] = getattr(self, name)
            #             continue
            #
            #         # -------------------------------------------------
            #         # 3️⃣ DEFAULT VALUE
            #         # -------------------------------------------------
            #         if param.default is not inspect.Parameter.empty:
            #             continue
            #
            #         # -------------------------------------------------
            #         # 4️⃣ HARD FAIL
            #         # -------------------------------------------------
            #         raise RuntimeError(
            #             f"Cannot resolve dependency '{name}' "
            #             f"for handler {handler_cls.__name__}"
            #         )
            #
            #     return handler_cls(**kwargs)
            #
            # handlers = build_handler_instances(handler_factory)

            self._action_bus = ActionBus(
                permission_validator=self.permission_validator,
                # handlers=handlers,
            )

        return self._action_bus

    @property
    def company_repository(self):
        if self._company_repo is None:
            self._company_repo = self._factory.company_repository()
        return self._company_repo

    @property
    def financial_record_repository(self):
        if self._record_repo is None:
            self._record_repo = self._factory.invoice_repository()
        return self._record_repo

    @property
    def financial_record_line_repository(self):
        if self._record_line_repo is None:
            self._record_line_repo = self._factory.invoice_line_repository()
        return self._record_line_repo

    @property
    def contract_repository(self):
        if self._contract_repo is None:
            self._contract_repo = self._factory.contract_repository()
        return self._contract_repo

    @property
    def contract_node_repository(self):
        if self._contract_node_repo is None:
            self._contract_node_repo = self._factory.contract_node_repository()
        return self._contract_node_repo

    @property
    def value_type_repository(self):
        if self._value_type_repo is None:
            self._value_type_repo = self._factory.value_type_repository()
        return self._value_type_repo

    @property
    def contract_snapshot_repository(self):
        if self._contract_snapshot_repo is None:
            self._contract_snapshot_repo = self._factory.contract_snapshot_repository()
        return self._contract_snapshot_repo

    @property
    def contract_node_snapshot_repository(self):
        if self._contract_node_snapshot_repo is None:
            self._contract_node_snapshot_repo = self._factory.contract_node_snapshot_repository()
        return self._contract_node_snapshot_repo

    @property
    def contract_node_value_snapshot_repository(self):
        if self._contract_node_value_snapshot_repo is None:
            self._contract_node_value_snapshot_repo = self._factory.contract_node_value_snapshot_repository()
        return self._contract_node_value_snapshot_repo

    @property
    def organization_repository(self) :
        if self._organization_repo is None:
            self._organization_repo = self._factory.organization_repository()
        return self._organization_repo


    @property
    def organization_user_repository(self) :
        if self._organization_user_repo is None:
            self._organization_user_repo = self._factory.organization_user_repository()
        return self._organization_user_repo

    @property
    def user_repository(self) :
        if self._user_repo is None:
            self._user_repo = self._factory.user_repository()
        return self._user_repo

    @property
    def document_repository(self) :
        if self._document_repo is None:
            self._document_repo = self._factory.document_repository()
        return self._document_repo

    @property
    def number_sequence_repository(self) :
        if self._number_sequence_repo is None:
            self._number_sequence_repo = self._factory.number_sequence_repository()
        return self._number_sequence_repo

    # ---------- domain services ----------
    @property
    def open_ai_invoice_service(self):
        if self._open_ai_invoice_service is None:
            from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.ocr_pdf_document_parser import (
                OpenAIInvoiceClient,
            )
            self._open_ai_invoice_service = OpenAIInvoiceClient()
        return self._open_ai_invoice_service


    # @property
    # def company_resolver(self):
    #     if self._company_resolver is None:
    #         self._company_resolver = CompanyResolveService(
    #             self.company_repository,
    #             ExactNipCandidateProvider(self.company_repository),self.open_ai_invoice_service)
    #     return self._company_resolver

    @property
    def financial_record_ingest_orchestrator(self):
        if self._financial_record_ingest_orchestrator is None:
            self._financial_record_ingest_orchestrator = FinancialRecordIngestOrchestrator(
                record_ingest_service_document=PdfFinancialRecordIngestService(self.financial_record_repository),
                record_ingest_service_excel=ExcelFinancialRecordIngestService(
                    self.financial_record_repository,
                    self.document_repository,
                    DocumentFileOrganizer(),
                    NumberGenerator(
                        number_sequence_repository=self.number_sequence_repository
                    )
                ),
                record_line_service=FinancialRecordLineUpdateService(
                    self.financial_record_line_repository,
                    self.contract_repository,
                    self.contract_node_repository,
                    self.value_type_repository,
                ),
                record_repository=self.financial_record_repository,
                file_workflow= self.record_file_workflow_service,
                record_completion_validator=RecordCompletionValidator()
            )
        return self._financial_record_ingest_orchestrator

    @property
    def record_file_workflow_service(self):
        if self._record_file_workflow_service is None:
            self._record_file_workflow_service = RecordFileWorkflowService(
                # record_repository=self.financial_record_repository,
                company_repository=self.company_repository,
                document_repository=self.document_repository,
                file_organizer=RecordFileOrganizer()
            )
        return self._record_file_workflow_service

    @property
    def company_evaluate_orchestrator(self):
        if self._company_evaluate_orchestrator is None:
            self._company_evaluate_orchestrator = CompanyEvaluateOrchestrator(
                self.company_repository,
                CompositeCompanyCandidateProvider(
                    [ExactNipCandidateProvider(self.company_repository),
                     BankAccountCandidateProvider(self.company_repository),
                     EmailCandidateProvider(self.company_repository),
                     StreetCandidateProvider(self.company_repository),
                     NameCandidateProvider(self.company_repository),
                     PhoneCandidateProvider(self.company_repository)
                     ]
                ),  self.open_ai_invoice_service )
        return self._company_evaluate_orchestrator

    # @property
    # def parse_invoice_from_file(self):
    #     if self._parse_invoice_from_file is None:
    #         from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.ocr_pdf_document_parser import (
    #             OCRAIAgentDocumentParser,
    #         )
    #
    #         self._parse_invoice_from_file = ParseInvoiceFromFileService(
    #             parser=OCRAIAgentDocumentParser(),
    #             company_evaluate_orchestrator=self.company_evaluate_orchestrator,
    #
    #             # company_resolve_service=self.company_resolver,
    #             record_file_organizer=RecordFileOrganizer(),
    #             # company_repository=self.company_repository,
    #             normalizer=self._normalizer,
    #             orchestrator=self.financial_record_ingest_orchestrator,
    #         )
    #     return self._parse_invoice_from_file

    @property
    def apply_financial_record_excel_batch(self):
        if self._apply_financial_record_excel_batch is None:
            self._apply_financial_record_excel_batch = ApplyFinancialRecordExcelBatchService(
                FinancialRecordExcelBatchResolver(company_evaluate_orchestrator=self.company_evaluate_orchestrator),
                ApplyCompanyExcelBatchService(self.company_repository,self.create_company),
                self.financial_record_ingest_orchestrator,
            )
        return self._apply_financial_record_excel_batch


    @property
    def document_parse_worker(self):
        if self._document_parse_worker is None:
            self._document_parse_worker = DocumentParseWorker(
            rpm=3,
            timeout=180,
            )
        return self._document_parse_worker


    @property
    def generate_financial_record_assignment_bundle(self):
        if self._generate_financial_record_assignment_bundle is None:
            self._generate_financial_record_assignment_bundle = GenerateFinancialRecordAssignmentBundleService(
                self.financial_record_repository,
                self.financial_record_line_repository,
                self.company_repository,
                self.contract_repository,
                self.contract_node_repository,
                self.value_type_repository,
            )
        return self._generate_financial_record_assignment_bundle
    @property
    def export_financial_record_assignment_excel_service(self):
        if self._export_financial_record_assignment_excel is None:
            self._export_financial_record_assignment_excel = ExportFinancialRecordAssignmentExcelService(
                exporter=ExcelInvoiceAssignmentExporter(
                                    self.contract_repository,
                                    self.contract_node_repository,
                                    self.value_type_repository,
                                )
            )
        return self._export_financial_record_assignment_excel

    @property
    def create_system_contract(self):
        if self._create_system_contract is None:
            self._create_system_contract =  CreateSystemContractOrchestrator(
                contract_repository=self.contract_repository,
                create_contract_service=self.create_contract
            )
        return self._create_system_contract

    @property
    def create_company(self):
        if self._create_company_service is None:
            self._create_company_service = CreateCompanyService(
                self.company_repository,
                self.create_system_contract
            )
        return self._create_company_service

    @property
    def update_company_service(self):
        if self._update_company_service is None:
            self._update_company_service = UpdateCompanyService(self.company_repository)
        return self._update_company_service

    @property
    def create_value_type(self):
        if self._create_value_type is None:
            self._create_value_type = CreateValueTypeService(self.value_type_repository)
        return self._create_value_type

    @property
    def create_contract(self):
        if self._create_contract is None:
            self._create_contract = CreateContractService(
                self.contract_repository,
                self.contract_node_repository,
                DefaultContractNodeTreeBuilder(),
                ContractNodeEntityValidator(),
            )
        return self._create_contract

    # @property
    # def update_contract(self):
    #     if self._update_contract_service is None:
    #         self._update_contract_service = UpdateContractService(self.contract_repository)
    #     return self._update_contract_service


    @property
    def update_contract_structure_service(self):
        if self._update_contract_structure_service is None:
            self._update_contract_structure_service = UpdateContractStructureService(
                self.contract_repository,
                self.contract_node_repository,
                DefaultContractNodeTreeBuilder(),
                ContractNodeEntityValidator(),
            )
        return self._update_contract_structure_service

    # @property
    # def generate_contract_structure_bundle(self):
    #     if self._generate_contract_structure_bundle is None:
    #         self._generate_contract_structure_bundle = GenerateContractStructureBundleService(
    #             self.contract_repository,
    #             self.cost_node_repository,
    #         )
    #     return self._generate_contract_structure_bundle

    # @property
    # def export_contract_structure_excel(self):
    #     if self._export_contract_structure_excel is None:
    #         self._export_contract_structure_excel = ExportContractStructureExcelService(
    #             excel=   ContractStructureExcelGenerator()
    #         )
    #     return self._export_contract_structure_excel

    @property
    def apply_contract_structure_excel(self):
        if self._apply_contract_structure_excel is None:
            self._apply_contract_structure_excel = ApplyContractStructureExcelService(
                self.create_contract,
                self.update_contract_structure_service,
                self.company_evaluate_orchestrator,
            )
        return self._apply_contract_structure_excel

    @property
    def contract_cost_report(self):
        if self._contract_cost_report is None:
            from contract_costs.services.reports.contract_cost_report_service import (
                ContractCostReportService,
            )
            self._contract_cost_report = ContractCostReportService(
                self.contract_repository,
                self.financial_record_line_repository,
                self.contract_node_repository,
                self.value_type_repository
            )
        return self._contract_cost_report

    @property
    def financial_record_query_service(self):
        if self._financial_record_query_service is None:
            self._financial_record_query_service = FinancialRecordDetailsQueryService(
                record_repo=self.financial_record_repository,
                record_line_repo=self.financial_record_line_repository,
                company_repo=self.company_repository,
                contract_repo=self.contract_repository,
                contract_node_repo=self.contract_node_repository,
                value_type_repo=self.value_type_repository,
            )
        return self._financial_record_query_service

    @property
    def review_query_service(self):
        if self._review_query_service is None:
            self._review_query_service = FinancialRecordReviewListQueryService(
                record_repo=self.financial_record_repository,
                record_line_repo=self.financial_record_line_repository,
                company_repo=self.company_repository,
                contract_repo=self.contract_repository
            )
        return self._review_query_service

    @property
    def financial_record_excel_export_service(self):
        if self._financial_record_excel_export_service is None:
            self._financial_record_excel_export_service = FinancialRecordExcelExportService(
                review_query_service=self.review_query_service,
                exporter=BaseExcelExporter()
            )
        return self._financial_record_excel_export_service

    # @property
    # def invoice_seller_summary_query_service(self):
    #     if self._invoice_seller_summary_query_service is None:
    #         self._invoice_seller_summary_query_service = InvoiceSellerSummaryQueryService(
    #             invoice_repo=self.invoice_repository,
    #             invoice_line_repo=self.invoice_line_repository,
    #             company_repo=self.company_repository,
    #         )
    #     return self._invoice_seller_summary_query_service


    @property
    def financial_record_action_service(self):
        if self._financial_record_action_service is None:
            self._financial_record_action_service = FinancialRecordActionService(
                self.financial_record_repository
            )
        return self._financial_record_action_service

    @property
    def financial_record_action_excel_loader(self):
        if self._financial_record_action_excel_loader is None:
            self._financial_record_action_excel_loader = FinancialRecordActionExcelLoader()
        return self._financial_record_action_excel_loader

    @property
    def company_query_service(self):
        if self._company_query_service is None:
            self._company_query_service = CompanyQueryService(
                self.company_repository
            )
        return self._company_query_service
    @property
    def activate_company_service(self):
        if self._activate_company_service is None:
            self._activate_company_service = ActivateCompanyService(
                self.company_repository
            )
        return self._activate_company_service
    @property
    def deactivate_company_service(self):
        if self._deactivate_company_service is None:
            self._deactivate_company_service = DeactivateCompanyService(
                self.company_repository
            )
        return self._deactivate_company_service


    @property
    def apply_companies_from_excel_service(self):
        if self._apply_companies_from_excel_service is None:
            self._apply_companies_from_excel_service = ApplyCompaniesFromExcelService(
                create_company_service=self.create_company,
                update_company_service=self.update_company_service,
                activate_company_service=self.activate_company_service,
                deactivate_company_service=self.deactivate_company_service,
            )
        return self._apply_companies_from_excel_service

    @property
    def value_type_query_service(self):
        if self._value_type_query_service is None:
            self._value_type_query_service = ValueTypeQueryService(
                self.value_type_repository
            )
        return self._value_type_query_service

    @property
    def deactivate_value_type_service(self):
        if self._deactivate_value_type_service is None:
            self._deactivate_value_type_service = DeactivateValueTypeService(
                self.value_type_repository
            )
        return self._deactivate_value_type_service

    @property
    def update_value_type_service(self):
        if self._update_value_type_service is None:
            self._update_value_type_service = UpdateValueTypeService(
                self.value_type_repository
            )
        return self._update_value_type_service

    @property
    def change_value_type_code_service(self):
        if self._change_value_type_code_service is None:
            self._change_value_type_code_service = ChangeValueTypeCodeService(
                self.value_type_repository
            )
        return self._change_value_type_code_service

    @property
    def contract_prepare_excel_exporter(self):
        if self._contract_prepare_excel_exporter is None:
            self._contract_prepare_excel_exporter = ContractPrepareExcelExporter()
        return self._contract_prepare_excel_exporter

    @property
    def set_contract_status_service(self):
        if self._set_contract_status_service is None:
            self._set_contract_status_service = SetContractStatusService(
                self.contract_repository
            )
        return self._set_contract_status_service

    @property
    def contract_prepare_progress_excel_exporter(self):
        if self._contract_prepare_progress_excel_exporter is None:
            self._contract_prepare_progress_excel_exporter = ContractPrepareProgressExcelExporter()
        return self._contract_prepare_progress_excel_exporter

    @property
    def apply_contract_progress_service(self):
        if self._apply_contract_progress_service is None:
            self._apply_contract_progress_service = ApplyContractProgressService(
                contract_repository=self.contract_repository,
                contract_node_repository=self.contract_node_repository,
            )
        return self._apply_contract_progress_service

    @property
    def apply_contract_progress_excel(self):
        if self._apply_contract_progress_excel is None:
            self._apply_contract_progress_excel = ApplyContractProgressExcelService(
                # contract_node_repository=self.contract_node_repository
                apply_contract_progress_service=self.apply_contract_progress_service
            )
        return self._apply_contract_progress_excel

    @property
    def create_contract_snapshot(self):
        if self._create_contract_snapshot is None:
            self._create_contract_snapshot = CreateContractSnapshotService(
                contract_repo=self.contract_repository,
                contract_node_repo=self.contract_node_repository,
                invoice_line_repo=self.financial_record_line_repository,
                snapshot_repo=self.contract_snapshot_repository,
                node_snapshot_repo=self.contract_node_snapshot_repository,
                value_snapshot_repo=self.contract_node_value_snapshot_repository
            )
        return self._create_contract_snapshot

    @property
    def contract_snapshot_query_service(self):
        if self._contract_snapshot_query_service is None:
            self._contract_snapshot_query_service = ContractSnapshotQueryService(
                contract_repo=self.contract_repository,
                contract_node_repo=self.contract_node_repository,
                value_type_repo=self.value_type_repository,
                snapshot_repo=self.contract_snapshot_repository,
                node_snapshot_repo=self.contract_node_snapshot_repository,
                value_snapshot_repo=self.contract_node_value_snapshot_repository,
            )
        return self._contract_snapshot_query_service

    @property
    def list_contracts_service(self):
        if self._list_contracts_service is None:
            self._list_contracts_service = ListContractsQueryService(
                contract_repo=self.contract_repository,
                contract_node_repo=self.contract_node_repository,
                record_line_repo=self.financial_record_line_repository,
                value_type_repo=self.value_type_repository,
            )
        return self._list_contracts_service

    @property
    def contract_details_service(self):
        if self._contract_details_service is None:
            self._contract_details_service = ContractDetailsQueryService(
                contract_repo=self.contract_repository,
                contract_node_repo=self.contract_node_repository,
                record_line_repo=self.financial_record_line_repository,
                value_type_repo=self.value_type_repository,
            )
        return self._contract_details_service
    @property
    def contract_query_service(self):
        if self._contract_query_service is None:
            self._contract_query_service = ContractQueryService(
                list_contracts_service = self.list_contracts_service,
                contract_details_service =self.contract_details_service,
            )
        return self._contract_query_service

    @property
    def create_organization_with_owner(self):
        if self._create_organization_with_owner is None:
            self._create_organization_with_owner = CreateOrganizationWithOwnerService(
                organization_repo=self.organization_repository,
                organization_user_repo=self.organization_user_repository,
                user_repo=self.user_repository,
            )
        return self._create_organization_with_owner

    @property
    def show_organizations(self):
        if self._show_organizations is None:
            self._show_organizations = ShowOrganizationsQueryService(
                organization_repo=self.organization_repository,
                organization_user_repo=self.organization_user_repository,
            )
        return self._show_organizations

    @property
    def context(self) -> ContextProvider:
        return self._context

    @property
    def use_organization(self):
        return UseOrganizationService(
            organization_repo=self.organization_repository,
            organization_user_repo=self.organization_user_repository,
            context=self.context,
        )

    @property
    def show_organization_users(self):
        if self._show_organization_users is None:
            self._show_organization_users = ShowOrganizationUsersQueryService(
                organization_user_repo=self.organization_user_repository,
                user_repo=self.user_repository,
            )
        return self._show_organization_users

    @property
    def add_organization_user(self):
        if self._add_organization_user is None:
            self._add_organization_user = AddOrganizationUserService(
                organization_repo=self.organization_repository,
                user_repo=self.user_repository,
                organization_user_repo=self.organization_user_repository,
            )
        return self._add_organization_user

    @property
    def create_user(self):
        if self._create_user is None:
            self._create_user = CreateUserService(
                user_repo=self.user_repository,
            )
        return self._create_user

    @property
    def remove_organization_user(self):
        if self._remove_organization_user is None:
            self._remove_organization_user = RemoveOrganizationUserService(
                organization_user_repo=self.organization_user_repository
            )
        return self._remove_organization_user

    @property
    def change_organization_user_role(self):
        if self._change_organization_user_role is None:
            from contract_costs.services.identity.change.change_organization_user_role_service import (
                ChangeOrganizationUserRoleService,
            )
            self._change_organization_user_role = ChangeOrganizationUserRoleService(
                organization_user_repo=self.organization_user_repository
            )
        return self._change_organization_user_role

    @property
    def deactivate_organization_user(self):
        if self._deactivate_organization_user is None:
            from contract_costs.services.identity.deactivate.deactivate_organization_user_service import (
                DeactivateOrganizationUserService,
            )
            self._deactivate_organization_user = DeactivateOrganizationUserService(
                organization_user_repo=self.organization_user_repository
            )
        return self._deactivate_organization_user

    @property
    def accept_organization_invite(self):
        if self._accept_organization_invite is None:
            from contract_costs.services.identity.accept.accept_organization_invite_service import (
                AcceptOrganizationInviteService,
            )
            self._accept_organization_invite = AcceptOrganizationInviteService(
                organization_user_repo=self.organization_user_repository
            )
        return self._accept_organization_invite

    @property
    def upload_document_service(self):
        if self._upload_document_service is None:
            from contract_costs.services.documents.upload.upload_document_service import (
                UploadDocumentService,
            )

            self._upload_document_service = UploadDocumentService(
                document_repository=self.document_repository,
            )

        return self._upload_document_service

    @property
    def document_parser_resolver(self):
        if self._document_parser_resolver is None:
            from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.ocr_pdf_document_parser import (
                OCRAIAgentDocumentParser,
            )
            from contract_costs.ksef.parser.ksef_document_parser import KsefDocumentParser
            self._document_parser_resolver = DefaultDocumentParserResolver(
                pdf_parser=OCRAIAgentDocumentParser(),
                ksef_parser=KsefDocumentParser(),
                image_parser=OCRAIAgentDocumentParser(),
            )
        return self._document_parser_resolver

    @property
    def parse_document_from_file(self):
        if self._parse_document_from_file is None:
            self._parse_document_from_file = ParseDocumentFromFileService(
                parser_resolver=self.document_parser_resolver
            )
        return self._parse_document_from_file

    @property
    def process_document_service(self):
        if self._process_document_service is None:
            from contract_costs.services.documents.process.process_document_service import (
                ProcessDocumentService,
            )

            self._process_document_service = ProcessDocumentService(
                document_repository=self.document_repository,
                parse_service=self.parse_document_from_file
                )

        return self._process_document_service

    @property
    def delete_document_service(self):
        if self._delete_document_service is None:
            self._delete_document_service = DeleteDocumentService(
                documents=self.document_repository
            )
        return self._delete_document_service

    @property
    def prepare_documents_service(self):
        if self._prepare_documents_service is None:
            from contract_costs.services.documents.prepare.prepare_documents_service import (
                PrepareDocumentsService,
            )

            self._prepare_documents_service = PrepareDocumentsService(
                document_repository=self.document_repository,
                record_repository=self.financial_record_repository,
                company_evaluate=self.company_evaluate_orchestrator
            )

        return self._prepare_documents_service

    @property
    def list_documents_query_service(self):
        if self._list_documents_query_service is None:
            self._list_documents_query_service = ListDocumentsQueryService(
                document_repository=self.document_repository
            )
        return self._list_documents_query_service

    @property
    def reprocess_document_service(self):
        if self._reprocess_document_service is None:
            self._reprocess_document_service = ReprocessDocumentService(
                documents=self.document_repository,
                action_bus=self.action_bus,
                process_document_service=self.process_document_service
            )
        return self._reprocess_document_service


    @property
    def export_document_assignment_excel_service(self):
        if self._export_document_assignment_excel_service is None:
            from contract_costs.services.documents.prepare.document_prepare_excel_export_service import (
                DocumentPrepareExcelExportService,
            )

            self._export_document_assignment_excel_service = (
                DocumentPrepareExcelExportService()
            )

        return self._export_document_assignment_excel_service

    @property
    def create_record_service(self):
        if self._create_record_service is None:
            self._create_record_service = CreateRecordFromDocumentService(
                company_evaluate=self.company_evaluate_orchestrator,
                normalizer=self._normalizer,
                ingest_orchestrator=self.financial_record_ingest_orchestrator,
                record_file_organizer=RecordFileOrganizer(),
                document_repository=self.document_repository,
                record_repository=self.financial_record_repository,
                file_workflow=self.record_file_workflow_service

            )
        return self._create_record_service

    @property
    def apply_document_service(self):
        if self._apply_document_service is None:
            self._apply_document_service = ApplyDocumentService(
                document_repo=self.document_repository,
                record_repo=self.financial_record_repository,
                company_evaluator=self.company_evaluate_orchestrator,
                create_record_service=self.create_record_service,
                file_organizer=DocumentFileOrganizer(),
                file_service=self.record_file_workflow_service,

            )
        return self._apply_document_service

    @property
    def document_action_excel_loader_service(self):
        if self._document_action_excel_loader_service is None:
            self._document_action_excel_loader_service = DocumentActionExcelLoader()

        return self._document_action_excel_loader_service
    @property
    def backfill_system_contracts(self):
        return BackfillSystemContractsService(
            company_repository=self.company_repository,
            create_system_contract=self.create_system_contract
    )
    # @staticmethod
    # def current_user_id() -> UUID:
    #     session = load_session()
    #     if not session:
    #         raise RuntimeError("Not logged in. Run: login <user>")
    #
    #     return UUID(session["user_id"])

_services: Dict[str, Services] = {}

def get_services(env: str = "prod") -> Services:
    if env not in _services:
        backend = (
            RepoBackend.MEMORY
            if env in {"memory"}
            else RepoBackend.MYSQL
        )
        context = FileContextProvider()

        _services[env] = Services(
            backend=backend,
            context_provider=context,
        )
    return _services[env]
