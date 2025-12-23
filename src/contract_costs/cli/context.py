from contract_costs.builders.cost_node_tree_builder import DefaultCostNodeTreeBuilder
from contract_costs.config import INVOICE_INPUT_DIR
from contract_costs.repository.cost_progress_snapshot_repository import CostProgressSnapshotRepository
from contract_costs.repository.mysql.cost_node_repository import MySQLCostNodeRepository
from contract_costs.repository.mysql.cost_progress_snapshot_repository import MySQLCostProgressSnapshotRepository
from contract_costs.repository.mysql.cost_type_repository import MySQLCostTypeRepository

from contract_costs.repository.mysql.invoice_line_repository import MySQLInvoiceLineRepository
from contract_costs.repository.mysql.invoice_repository import MySQLInvoiceRepository
from contract_costs.repository.mysql.company_repository import MySQLCompanyRepository
from contract_costs.repository.mysql.contract_repository import MySQLContractRepository
from contract_costs.services.catalogues.invoice_file_organizer import InvoiceFileOrganizer
from contract_costs.services.companies.update_company_service import UpdateCompanyService

from contract_costs.services.companies.create_company_service import (
    CreateCompanyService,
)
from contract_costs.services.contracts.apply_contract_structure_excel import ApplyContractStructureExcelService
from contract_costs.services.contracts.create_contract_service import CreateContractService
from contract_costs.services.contracts.export.contract_structure_excel_generator import ContractStructureExcelGenerator
from contract_costs.services.contracts.generate_contract_structure_excel import GenerateContractStructureExcelService

from contract_costs.services.contracts.update_contract_structure_service import UpdateContractStructureService
from contract_costs.services.contracts.validators.cost_node_tree_validator import CostNodeEntityValidator

from contract_costs.services.cost_types.create_cost_type_service import (
    CreateCostTypeService,
)

from contract_costs.services.invoices.apply_invoice_excel_batch_service import (
    ApplyInvoiceExcelBatchService,
)

from contract_costs.services.invoices.company_resolve_service import CompanyResolveService
from contract_costs.services.invoices.excel.invoice_excel_resolver import InvoiceExcelBatchResolver
from contract_costs.services.invoices.export.excel_invoice_assignment_exporter import ExcelInvoiceAssignmentExporter
from contract_costs.services.invoices.generate_assignment_service import GenerateInvoiceAssignmentService
from contract_costs.services.invoices.invoice_line_update_service import InvoiceLineUpdateService
from contract_costs.services.invoices.invoice_update_service import InvoiceUpdateService
from contract_costs.services.invoices.parse_invoice_from_file import ParseInvoiceFromFileService


class Services:
    def __init__(self) -> None:
        self._company_repository = None
        self._create_company = None
        self._update_company_service = None

        self._invoice_repository = None
        self._invoice_line_repository = None

        self._cost_type_repository = None
        self._create_cost_type = None

        self._contract_repository = None
        self._cost_node_repository = None
        self._create_contract = None
        self._update_contract_service = None

        self._company_resolver = None
        self._parse_invoice_from_file = None
        self._invoice_repo = None
        self._invoice_line_repo = None

        self._invoice_watcher_service = None
        self._create_cost_type = None
        self._cost_type_repository = None

        self._generate_contract_structure_excel = None

        self._apply_contract_structure_excel = None
        self._update_contract_structure_service= None

        self._cost_progress_snapshot_repository = None

        self._generate_invoice_assignment_excel = None


    @property
    def company_repository(self):
        if self._company_repository is None:
            self._company_repository = MySQLCompanyRepository()
        return self._company_repository

    @property
    def create_company(self):
        if self._create_company is None:
            self._create_company = CreateCompanyService(self.company_repository)
        return self._create_company

    @property
    def update_company_service(self):
        if self._update_company_service is None:
            self._update_company_service = UpdateCompanyService(self.company_repository)
        return self._update_company_service

    @property
    def contract_repository(self):
        if self._contract_repository is None:
            self._contract_repository = MySQLContractRepository()
        return self._contract_repository

    @property
    def cost_node_repository(self):
        if self._cost_node_repository is None:
            self._cost_node_repository = MySQLCostNodeRepository()
        return self._cost_node_repository

    @property
    def create_contract(self):
        if self._create_contract is None:
            self._create_contract = CreateContractService(
                self.contract_repository,
                self.cost_node_repository,
                DefaultCostNodeTreeBuilder(),
                CostNodeEntityValidator()
            )
        return self._create_contract

    # @property
    # def update_contract(self):
    #     if self._update_contract_service is None:
    #         self._update_contract_service = UpdateContractService(self._contract_repository)

    @property
    def company_resolver(self):
        if self._company_resolver is None:
            self._company_resolver = CompanyResolveService(self.company_repository)
        return self._company_resolver

    @property
    def invoice_repository(self):
        if self._invoice_repository is None:
            self._invoice_repository = MySQLInvoiceRepository()
        return self._invoice_repository

    @property
    def invoice_line_repository(self):
        if self._invoice_line_repository is None:
            self._invoice_line_repository = MySQLInvoiceLineRepository()
        return self._invoice_line_repository

    @property
    def cost_type_repository(self):
        if self._cost_type_repository is None:
            self._cost_type_repository = MySQLCostTypeRepository()
        return self._cost_type_repository

    @property
    def create_cost_type(self):
        if self._create_cost_type is None:
            self._create_cost_type = CreateCostTypeService(self.cost_type_repository)
        return self._create_cost_type

    @property
    def update_contract_structure_service(self):
        if self._update_contract_structure_service is None:
            self._update_contract_structure_service = UpdateContractStructureService(
                self.contract_repository,
                self.cost_node_repository,
                DefaultCostNodeTreeBuilder(),
                CostNodeEntityValidator()
            )
        return self._update_contract_structure_service

    @property
    def apply_contract_structure_excel(self):
        if self._apply_contract_structure_excel is None:
            self._apply_contract_structure_excel = ApplyContractStructureExcelService(
                self.create_contract,self.update_contract_structure_service,self.company_resolver)
        return self._apply_contract_structure_excel


    @property
    def generate_contract_structure_excel(self):
        if self._generate_contract_structure_excel is None:
            self._generate_contract_structure_excel = GenerateContractStructureExcelService(
                self.contract_repository,
                self.cost_node_repository,
                ContractStructureExcelGenerator(),
            )
        return self._generate_contract_structure_excel

    @property
    def parse_invoice_from_file(self):
        if self._parse_invoice_from_file is None:
            from contract_costs.services.invoices.parsers.ocr_pdf_invoice_parser import (
                OCRAIAgentInvoiceParser,
            )

            self._parse_invoice_from_file = ParseInvoiceFromFileService(
                parser=OCRAIAgentInvoiceParser(),
                company_resolve_service=self.company_resolver,
                invoice_update_service=InvoiceUpdateService(self.invoice_repository),
                invoice_line_update_service=InvoiceLineUpdateService(self.invoice_line_repository),
                invoice_file_organizer=InvoiceFileOrganizer(),
                company_repository=self.company_repository,
            )
        return self._parse_invoice_from_file

    @property
    def apply_invoice_excel_batch(self):
        return ApplyInvoiceExcelBatchService(
            InvoiceUpdateService(self.invoice_repository),
            InvoiceLineUpdateService(self.invoice_line_repository,
                                     self.contract_repository,
                                     self.cost_node_repository,
                                     self.cost_type_repository,

                                     ),
            InvoiceExcelBatchResolver(self.company_resolver)
        )

    @property
    def invoice_watcher_service(self):
        if self._invoice_watcher_service is None:
            from contract_costs.services.watcher.invoice_watcher_service import (
                InvoiceWatcherService,
            )

            self._invoice_watcher_service = InvoiceWatcherService(
                watch_dir=INVOICE_INPUT_DIR,
                parse_invoice_service=self.parse_invoice_from_file,
            )
        return self._invoice_watcher_service

    @property
    def cost_progerss_snapshot_repository(self):
        if self._cost_progress_snapshot_repository is None:
            self._cost_progress_snapshot_repository = MySQLCostProgressSnapshotRepository()
        return self._cost_progress_snapshot_repository

    @property
    def generate_invoice_assignment_excel(self):
        if self._generate_invoice_assignment_excel is None:
            self._generate_invoice_assignment_excel = GenerateInvoiceAssignmentService(
                self.invoice_repository,
                self.invoice_line_repository,
                self.company_repository,
                self.contract_repository,
                self.cost_node_repository,
                self.cost_type_repository,
                ExcelInvoiceAssignmentExporter(
                    self.contract_repository,
                    self.cost_node_repository,
                    self.cost_type_repository
                )
            )
        return self._generate_invoice_assignment_excel


_services: Services | None = None


def get_services() -> Services:
    global _services
    if _services is None:
        _services = Services()
    return _services
