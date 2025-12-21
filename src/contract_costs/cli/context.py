from contract_costs.builders.cost_node_tree_builder import DefaultCostNodeTreeBuilder
from contract_costs.config import INVOICE_INPUT_DIR
from contract_costs.repository.mysql.cost_type import MySQLCostTypeRepository

from contract_costs.repository.inmemory.cost_node_repository import InMemoryCostNodeRepository
from contract_costs.repository.inmemory.invoice_line_repository import InMemoryInvoiceLineRepository
from contract_costs.repository.inmemory.invoice_repository import InMemoryInvoiceRepository
from contract_costs.repository.mysql.company_repository import MySQLCompanyRepository
from contract_costs.repository.mysql.contract_repository import MySQLContractRepository
from contract_costs.services.catalogues.invoice_file_organizer import InvoiceFileOrganizer
from contract_costs.services.companies.change_company_role_service import ChangeCompanyRoleService

from contract_costs.services.companies.create_company_service import (
    CreateCompanyService,
)
from contract_costs.services.contracts.create_contract_service import CreateContractService

from contract_costs.services.cost_types.create_cost_type_service import (
    CreateCostTypeService,
)

from contract_costs.services.invoices.company_resolve_service import CompanyResolveService
from contract_costs.services.invoices.invoice_line_update_service import InvoiceLineUpdateService
from contract_costs.services.invoices.invoice_update_service import InvoiceUpdateService
from contract_costs.services.invoices.parse_invoice_from_file import ParseInvoiceFromFileService

# class Services:
#     def __init__(self) -> None:
#         self.company_repository = MySQLCompanyRepository()
#         self.create_company = CreateCompanyService(self.company_repository)
#         self.change_company_role = ChangeCompanyRoleService(self.company_repository)
#         self.cost_type_repository = InMemoryCostTypeRepository()
#         self.create_cost_type = CreateCostTypeService(
#             self.cost_type_repository
#         )
#         self.contract_repository = MySQLContractRepository()
#         self.cost_node_repository = InMemoryCostNodeRepository()
#         self.create_contract = CreateContractService(
#             self.contract_repository,
#             self.cost_node_repository,
#             DefaultCostNodeTreeBuilder(),
#         )
#         self.parse_invoice_from_file = ParseInvoiceFromFileService(
#             OCRAIAgentInvoiceParser(),
#             CompanyResolveService(self.company_repository),
#             InvoiceUpdateService(InMemoryInvoiceRepository()),
#             InvoiceLineUpdateService(InMemoryInvoiceLineRepository()),
#             InvoiceFileOrganizer(),
#             self.company_repository
#
#         )

class Services:
    def __init__(self) -> None:
        self._company_repository = None
        self._create_company = None
        self._change_company_role = None

        self._invoice_repository = None
        self._invoice_line_repository = None

        self._cost_type_repository = None
        self._create_cost_type = None

        self._contract_repository = None
        self._cost_node_repository = None
        self._create_contract = None

        self._company_resolver = None
        self._parse_invoice_from_file = None
        self._invoice_repo = None
        self._invoice_line_repo = None

        self._invoice_watcher_service = None
        self._create_cost_type = None
        self._cost_type_repository = None


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
    def change_company_role(self):
        if self._change_company_role is None:
            self._change_company_role = ChangeCompanyRoleService(self.company_repository)
        return self._change_company_role

    @property
    def contract_repository(self):
        if self._contract_repository is None:
            self._contract_repository = MySQLContractRepository()
        return self._contract_repository

    @property
    def cost_node_repository(self):
        if self._cost_node_repository is None:
            self._cost_node_repository = InMemoryCostNodeRepository()
        return self._cost_node_repository

    @property
    def create_contract(self):
        if self._create_contract is None:
            self._create_contract = CreateContractService(
                self.contract_repository,
                self.cost_node_repository,
                DefaultCostNodeTreeBuilder(),
            )
        return self._create_contract

    @property
    def company_resolver(self):
        if self._company_resolver is None:
            self._company_resolver = CompanyResolveService(self.company_repository)
        return self._company_resolver

    @property
    def invoice_repository(self):
        if self._invoice_repository is None:
            self._invoice_repository = InMemoryInvoiceRepository()
        return self._invoice_repository

    @property
    def invoice_line_repository(self):
        if self._invoice_line_repository is None:
            self._invoice_line_repository = InMemoryInvoiceLineRepository()
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

_services: Services | None = None


def get_services() -> Services:
    global _services
    if _services is None:
        _services = Services()
    return _services
