from contract_costs.builders.cost_node_tree_builder import DefaultCostNodeTreeBuilder
from contract_costs.config import INVOICE_INPUT_DIR
from contract_costs.infrastructure.excel.base_excel_exporter import BaseExcelExporter
from contract_costs.infrastructure.excel.invoice_action_excel_loader import InvoiceActionExcelLoader
from contract_costs.services.catalogues.invoice_file_organizer import InvoiceFileOrganizer
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
from contract_costs.services.contracts.apply.set_contract_status_service import SetContractStatusService
from contract_costs.services.contracts.create_contract_service import CreateContractService
# from contract_costs.services.contracts.export.export_contract_structure_excel_service import \
#     ExportContractStructureExcelService
from contract_costs.services.contracts.prepare.contract_prepare_excel_exporter import ContractPrepareExcelExporter
from contract_costs.services.contracts.update_contract_service import UpdateContractService
from contract_costs.services.contracts.apply.update_contract_structure_service import (
    UpdateContractStructureService,
)
from contract_costs.services.contracts.apply.apply_contract_structure_excel import (
    ApplyContractStructureExcelService,
)
# from contract_costs.services.contracts.generate_contract_structure_excel import (
#     GenerateContractStructureBundleService,
# )
# from contract_costs.services.contracts.export.contract_structure_excel_generator import (
#     ContractStructureExcelGenerator,
# )
from contract_costs.services.contracts.validators.cost_node_tree_validator import (
    CostNodeEntityValidator,
)
from contract_costs.services.cost_types.apply.change_cost_type_code_service import ChangeCostTypeCodeService
from contract_costs.services.cost_types.apply.deactivate_cost_type_service import DeactivateCostTypeService
from contract_costs.services.cost_types.apply.update_cost_type_service import UpdateCostTypeService
from contract_costs.services.cost_types.create_cost_type_service import CreateCostTypeService
from contract_costs.services.cost_types.query.cost_type_query_service import CostTypeQueryService
from contract_costs.services.invoices.actions.invoice_action_service import InvoiceActionService

from contract_costs.services.invoices.assigment.invoice_sources.excel.invoice_excel_resolver import InvoiceExcelBatchResolver
from contract_costs.services.invoices.assigment.invoice_sources.normalization.invoice_parser_normalizer import \
    InvoiceParseNormalizer
from contract_costs.services.invoices.assigment.prepare.export.export_invoice_assignment_excel_service import \
    ExportInvoiceAssignmentExcelService
from contract_costs.services.invoices.excel.invoice_excel_export_service import InvoiceExcelExportService
from contract_costs.services.invoices.queries.invoice_details_query_service import InvoiceDetailsQueryService
from contract_costs.services.invoices.queries.invoice_seller_summary_query_service import InvoiceSellerSummaryQueryService
from contract_costs.services.invoices.assigment.ingest.invoice_update_service import InvoiceUpdateService
from contract_costs.services.invoices.assigment.ingest.invoice_line_update_service import InvoiceLineUpdateService
from contract_costs.services.invoices.assigment.ingest.invoice_ingest_orchestrator import (
    InvoiceIngestOrchestrator,
)

from contract_costs.services.invoices.assigment.invoice_sources.pdf.parse_invoice_from_file import ParseInvoiceFromFileService
from contract_costs.services.invoices.assigment.apply.apply_invoice_excel_batch_service import (
    ApplyInvoiceExcelBatchService,
)
from contract_costs.services.invoices.assigment.apply.apply_company_excel_batch_service import (
    ApplyCompanyExcelBatchService,
)
from contract_costs.services.invoices.assigment.prepare.generate_assignment_bundle_service import (
    GenerateInvoiceAssignmentBundleService,
)
from contract_costs.services.invoices.assigment.prepare.export.excel_invoice_assignment_exporter import \
    ExcelInvoiceAssignmentExporter

from contract_costs.repository.factory.repository_factory import (
    RepositoryFactory,
    RepoBackend,
)
from typing import Dict

from contract_costs.services.invoices.review.invoice_review_list_query_service import InvoiceReviewListQueryService
from contract_costs.services.workers.ai_invoice_worker import InvoiceAIWorker


class Services:
    def __init__(self, backend: RepoBackend = RepoBackend.MYSQL) -> None:
        self._factory = RepositoryFactory(backend)

        # repos
        self._company_repo = None
        self._invoice_repo = None
        self._invoice_line_repo = None
        self._contract_repo = None
        self._cost_node_repo = None
        self._cost_type_repo = None
        self._cost_progress_snapshot_repo = None

        # services
        # self._company_resolver = None
        self._invoice_ingest_orchestrator = None
        self._parse_invoice_from_file = None
        self._apply_invoice_excel_batch = None
        self._invoice_watcher_service = None
        self._generate_invoice_assignment_bundle=None
        self._export_invoice_assignment_excel = None
        self._create_company_service = None
        self._update_company_service = None
        self._create_cost_type = None
        self._create_contract = None
        self._update_contract_service = None
        self._update_contract_structure_service = None
        self._apply_contract_structure_excel = None
        self._generate_contract_structure_bundle = None
        self._export_contract_structure_excel = None

        self._invoice_ai_worker = None

        self._contract_cost_report =None
        self._open_ai_invoice_service = None
        self._company_evaluate_orchestrator =None

        self._invoice_query_service = None

        self._invoice_seller_summary_query_service = None

        self._invoice_excel_export_service = None

        self._invoice_action_service = None
        self._invoice_action_excel_loader = None
        self._review_query_service = None
        self._apply_companies_from_excel_service = None

        self._company_query_service = None

        self._activate_company_service = None
        self._deactivate_company_service = None
        self._cost_type_query_service = None
        self._deactivate_cost_type_service = None
        self._update_cost_type_service = None
        self._change_cost_type_code_service = None
        self._contract_prepare_excel_exporter =None
        self._set_contract_status_service = None

        self._normalizer = InvoiceParseNormalizer()

    # ---------- repositories ----------

    @property
    def company_repository(self):
        if self._company_repo is None:
            self._company_repo = self._factory.company_repository()
        return self._company_repo

    @property
    def invoice_repository(self):
        if self._invoice_repo is None:
            self._invoice_repo = self._factory.invoice_repository()
        return self._invoice_repo

    @property
    def invoice_line_repository(self):
        if self._invoice_line_repo is None:
            self._invoice_line_repo = self._factory.invoice_line_repository()
        return self._invoice_line_repo

    @property
    def contract_repository(self):
        if self._contract_repo is None:
            self._contract_repo = self._factory.contract_repository()
        return self._contract_repo

    @property
    def cost_node_repository(self):
        if self._cost_node_repo is None:
            self._cost_node_repo = self._factory.cost_node_repository()
        return self._cost_node_repo

    @property
    def cost_type_repository(self):
        if self._cost_type_repo is None:
            self._cost_type_repo = self._factory.cost_type_repository()
        return self._cost_type_repo

    @property
    def cost_progress_snapshot_repository(self):
        if self._cost_progress_snapshot_repo is None:
            self._cost_progress_snapshot_repo = self._factory.cost_progress_snapshot_repository()
        return self._cost_progress_snapshot_repo


    # ---------- domain services ----------
    @property
    def open_ai_invoice_service(self):
        if self._open_ai_invoice_service is None:
            from contract_costs.services.invoices.assigment.invoice_sources.pdf.parsers.ocr_pdf_invoice_parser import (
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
    def invoice_ingest_orchestrator(self):
        if self._invoice_ingest_orchestrator is None:
            self._invoice_ingest_orchestrator = InvoiceIngestOrchestrator(
                invoice_service=InvoiceUpdateService(self.invoice_repository),
                invoice_line_service=InvoiceLineUpdateService(
                    self.invoice_line_repository,
                    self.contract_repository,
                    self.cost_node_repository,
                    self.cost_type_repository,
                ),
            )
        return self._invoice_ingest_orchestrator

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

    @property
    def parse_invoice_from_file(self):
        if self._parse_invoice_from_file is None:
            from contract_costs.services.invoices.assigment.invoice_sources.pdf.parsers.ocr_pdf_invoice_parser import (
                OCRAIAgentInvoiceParser,
            )

            self._parse_invoice_from_file = ParseInvoiceFromFileService(
                parser=OCRAIAgentInvoiceParser(),
                company_evaluate_orchestrator=self.company_evaluate_orchestrator,

                # company_resolve_service=self.company_resolver,
                invoice_file_organizer=InvoiceFileOrganizer(),
                company_repository=self.company_repository,
                normalizer=self._normalizer,
                orchestrator=self.invoice_ingest_orchestrator,
            )
        return self._parse_invoice_from_file

    @property
    def apply_invoice_excel_batch(self):
        if self._apply_invoice_excel_batch is None:
            self._apply_invoice_excel_batch = ApplyInvoiceExcelBatchService(
                InvoiceExcelBatchResolver( company_evaluate_orchestrator=self.company_evaluate_orchestrator),
                ApplyCompanyExcelBatchService(self.company_repository),
                self.invoice_ingest_orchestrator,
            )
        return self._apply_invoice_excel_batch

    @property
    def invoice_watcher_service(self):
        if self._invoice_watcher_service is None:
            from contract_costs.services.watcher.invoice_watcher import (
                InvoiceWatcherService,
            )
            self._invoice_watcher_service = InvoiceWatcherService(
                watch_dir=INVOICE_INPUT_DIR,
            )
        return self._invoice_watcher_service

    @property
    def invoice_ai_worker(self):
        if self._invoice_ai_worker is None:
            self._invoice_ai_worker = InvoiceAIWorker(
            rpm=3,
            timeout=180,
            )
        return self._invoice_ai_worker


    @property
    def generate_invoice_assignment_bundle(self):
        if self._generate_invoice_assignment_bundle is None:
            self._generate_invoice_assignment_bundle = GenerateInvoiceAssignmentBundleService(
                self.invoice_repository,
                self.invoice_line_repository,
                self.company_repository,
                self.contract_repository,
                self.cost_node_repository,
                self.cost_type_repository,
            )
        return self._generate_invoice_assignment_bundle
    @property
    def export_invoice_assignment_excel_service(self):
        if self._export_invoice_assignment_excel is None:
            self._export_invoice_assignment_excel = ExportInvoiceAssignmentExcelService(
                exporter=ExcelInvoiceAssignmentExporter(
                                    self.contract_repository,
                                    self.cost_node_repository,
                                    self.cost_type_repository,
                                )
            )
        return self._export_invoice_assignment_excel

    @property
    def create_company(self):
        if self._create_company_service is None:
            self._create_company_service = CreateCompanyService(self.company_repository)
        return self._create_company_service

    @property
    def update_company_service(self):
        if self._update_company_service is None:
            self._update_company_service = UpdateCompanyService(self.company_repository)
        return self._update_company_service

    @property
    def create_cost_type(self):
        if self._create_cost_type is None:
            self._create_cost_type = CreateCostTypeService(self.cost_type_repository)
        return self._create_cost_type

    @property
    def create_contract(self):
        if self._create_contract is None:
            self._create_contract = CreateContractService(
                self.contract_repository,
                self.cost_node_repository,
                DefaultCostNodeTreeBuilder(),
                CostNodeEntityValidator(),
            )
        return self._create_contract

    @property
    def update_contract(self):
        if self._update_contract_service is None:
            self._update_contract_service = UpdateContractService(self.contract_repository)
        return self._update_contract_service


    @property
    def update_contract_structure_service(self):
        if self._update_contract_structure_service is None:
            self._update_contract_structure_service = UpdateContractStructureService(
                self.contract_repository,
                self.cost_node_repository,
                DefaultCostNodeTreeBuilder(),
                CostNodeEntityValidator(),
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
                self.invoice_line_repository,
                self.cost_node_repository,
                self.cost_type_repository
            )
        return self._contract_cost_report

    @property
    def invoice_query_service(self):
        if self._invoice_query_service is None:
            self._invoice_query_service = InvoiceDetailsQueryService(
                invoice_repo=self.invoice_repository,
                invoice_line_repo=self.invoice_line_repository,
                company_repo=self.company_repository,
                contract_repo=self.contract_repository,
                cost_node_repo=self.cost_node_repository,
                cost_type_repo=self.cost_type_repository,
            )
        return self._invoice_query_service

    @property
    def review_query_service(self):
        if self._review_query_service is None:
            self._review_query_service = InvoiceReviewListQueryService(
                invoice_repo=self.invoice_repository,
                invoice_line_repo=self.invoice_line_repository,
                company_repo=self.company_repository,
            )
        return self._review_query_service

    @property
    def invoice_excel_export_service(self):
        if self._invoice_excel_export_service is None:
            self._invoice_excel_export_service = InvoiceExcelExportService(
                review_query_service=self.review_query_service,
                exporter=BaseExcelExporter()
            )
        return self._invoice_excel_export_service

    @property
    def invoice_seller_summary_query_service(self):
        if self._invoice_seller_summary_query_service is None:
            self._invoice_seller_summary_query_service = InvoiceSellerSummaryQueryService(
                invoice_repo=self.invoice_repository,
                invoice_line_repo=self.invoice_line_repository,
                company_repo=self.company_repository,
            )
        return self._invoice_seller_summary_query_service


    @property
    def invoice_action_service(self):
        if self._invoice_action_service is None:
            self._invoice_action_service = InvoiceActionService(
                self.invoice_repository
            )
        return self._invoice_action_service

    @property
    def invoice_action_excel_loader(self):
        if self._invoice_action_excel_loader is None:
            self._invoice_action_excel_loader = InvoiceActionExcelLoader()
        return self._invoice_action_excel_loader

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
    def cost_type_query_service(self):
        if self._cost_type_query_service is None:
            self._cost_type_query_service = CostTypeQueryService(
                self.cost_type_repository
            )
        return self._cost_type_query_service

    @property
    def deactivate_cost_type_service(self):
        if self._deactivate_cost_type_service is None:
            self._deactivate_cost_type_service = DeactivateCostTypeService(
                self.cost_type_repository
            )
        return self._deactivate_cost_type_service

    @property
    def update_cost_type_service(self):
        if self._update_cost_type_service is None:
            self._update_cost_type_service = UpdateCostTypeService(
                self.cost_type_repository
            )
        return self._update_cost_type_service

    @property
    def change_cost_type_code_service(self):
        if self._change_cost_type_code_service is None:
            self._change_cost_type_code_service = ChangeCostTypeCodeService(
                self.cost_type_repository
            )
        return self._change_cost_type_code_service

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

_services: Dict[str, Services] = {}

def get_services(env: str = "prod") -> Services:
    if env not in _services:
        backend = (
            RepoBackend.MEMORY
            if env in {"test", "tests", "memory"}
            else RepoBackend.MYSQL
        )
        _services[env] = Services(backend=backend)
    return _services[env]
