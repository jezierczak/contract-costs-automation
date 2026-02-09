from dataclasses import replace
import logging
from datetime import datetime
from typing import Callable
from uuid import UUID

from contract_costs.common.time import utc_now
from contract_costs.model.company import CompanyType
from contract_costs.model.financial_record import FinancialRecordStatus, FinancialRecord
from contract_costs.repository.financial_record_repository import FinancialRecordRepository
from contract_costs.repository.financial_record_line_repository import FinancialRecordLineRepository
from contract_costs.repository.company_repository import CompanyRepository
from contract_costs.repository.contract_repository import ContractRepository
from contract_costs.repository.contract_node_repository import ContractNodeRepository
from contract_costs.repository.value_type_repository import ValueTypeRepository
from contract_costs.services.documents.document_selector import DocumentSelector
from contract_costs.services.financial_records.assigment.apply.commands.invoice_command import InvoiceCommand

from contract_costs.services.financial_records.assigment.prepare.dto.assignment_export_bundle import (
    FinancialRecordAssignmentExportBundle,
)
from contract_costs.services.financial_records.assigment.prepare.dto.invoice_export import FinancialRecordExport
from contract_costs.services.financial_records.assigment.prepare.dto.invoice_line_export import FinancialRecordLineExport
from contract_costs.services.financial_records.assigment.prepare.dto.company_export import CompanyExport
from contract_costs.services.financial_records.assigment.prepare.dto.contract_export import ContractExport
from contract_costs.services.financial_records.assigment.prepare.dto.cost_node_export import CostNodeExport
from contract_costs.services.financial_records.assigment.prepare.dto.cost_type_export import CostTypeExport

logger = logging.getLogger(__name__)


class GenerateFinancialRecordAssignmentBundleService:

    def __init__(
        self,
        record_repository: FinancialRecordRepository,
        record_line_repository: FinancialRecordLineRepository,
        company_repository: CompanyRepository,
        contract_repository: ContractRepository,
        contract_node_repository: ContractNodeRepository,
        value_type_repository: ValueTypeRepository,
        clock: Callable[[], datetime] = utc_now,
        # exporter: InvoiceAssignmentExporter,
    ) -> None:
        self._record_repo = record_repository
        self._record_line_repo = record_line_repository
        self._company_repo = company_repository
        self._contract_repo = contract_repository
        self._contract_node_repo = contract_node_repository
        self._value_type_repo = value_type_repository
        self._clock = clock
        # self._exporter = exporter

    def execute(self,
                *,
                organization_id: UUID,
                actor_user_id: UUID,
                invoice_status: FinancialRecordStatus | list[FinancialRecordStatus]
                ) -> FinancialRecordAssignmentExportBundle:
        #  Dane główne

        # invoice_status = InvoiceStatus(status)
        financial_records: list[FinancialRecord] = self._record_repo.get_for_assignment(
            organization_id=organization_id,
            status=invoice_status)

        record_ids = [i.id for i in financial_records]

        record_references_from_ids = {i.id:i.reference for i in financial_records}

        updated_records: list[FinancialRecord] = []

        for record in financial_records:
            if record.status != FinancialRecordStatus.IN_PROGRESS:
                updated = replace(record,
                                  status=FinancialRecordStatus.IN_PROGRESS,
                                  updated_at = self._clock(),
                                  updated_by_user_id=actor_user_id
                                  )
                self._record_repo.update(updated)
                updated_records.append(updated)
            else:
                updated_records.append(record)

        record_lines = self._record_line_repo.list_by_financial_record_ids(
            organization_id=organization_id,
            financial_records_ids=record_ids)
        record_lines.extend(self._record_line_repo.list_unassigned(organization_id=organization_id))


        #  Companies (buyer + seller)

        # company_buyers = {
        #     inv.buyer_id for inv in updated_invoices}
        # company_sellers= {
        #     inv.seller_id for inv in updated_invoices
        # }

        # buyers = [
        #     CompanyExport(
        #         id=c.id,
        #         name=c.name,
        #         tax_number=c.tax_number,
        #     )
        #     for c in (self._company_repo.get(cid) for cid in company_buyers)
        #     if c is not None
        # ]
        # if len(buyers)==0:
        buyers = [
            CompanyExport(
                id=c.id,
                name=c.name,
                tax_number=c.tax_number,
            )
            for c in self._company_repo.get_owners(organization_id=organization_id)
        ]

        sellers = [
            CompanyExport(
                id=c.id,
                name=c.name,
                tax_number=c.tax_number,
            )
            for c in self._company_repo.list_all(organization_id=organization_id)
            # for c in (self._company_repo.get(cid) for cid in company_sellers)
            if c is not None and c.role != CompanyType.OWN
        ]

        #  Contracts
        contracts = [
            ContractExport(
                id=c.id,
                name=c.name,
                code=c.code,
            )
            for c in self._contract_repo.list(organization_id=organization_id)
        ]

        #  Cost nodes
        contract_code_by_id = {
            c.id: c.code
            for c in contracts
        }

        cost_nodes = []

        for n in self._contract_node_repo.list_leaf_nodes_for_active_contracts(organization_id=organization_id):
            contract_code = contract_code_by_id.get(n.contract_id)
            if contract_code is None:
                raise RuntimeError(
                    f"Missing contract code for contract_id={n.contract_id}"
                )

            cost_nodes.append(
                CostNodeExport(
                    id=n.id,
                    contract_id=n.contract_id,
                    parent_id=n.parent_id,
                    code=n.code,
                    name=n.name,
                    budget=n.budget,
                    contract_code=contract_code,
                )
            )

        #  Cost types
        cost_types = [
            CostTypeExport(
                id=ct.id,
                code=ct.code,
                name=ct.name,
            )
            for ct in self._value_type_repo.list_all(organization_id=organization_id)
        ]

        #  Mapowanie faktur
        records_exports = []
        for i in updated_records:
            buyer = self._company_repo.get(organization_id=organization_id,company_id=i.buyer_id) if i.buyer_id else None
            seller = self._company_repo.get(organization_id=organization_id,company_id=i.seller_id) if i.seller_id else None

            records_exports.append(
                FinancialRecordExport(
                    action=InvoiceCommand.APPLY,
                    record_id=str(i.id),
                    reference=i.reference,
                    invoice_date=i.invoice_date,
                    selling_date=i.selling_date,
                    buyer_tax_number=buyer.tax_number if buyer else None,
                    seller_tax_number=seller.tax_number if seller else None,
                    payment_method=i.payment_method,
                    payment_status=i.payment_status,
                    status=i.status,
                    due_date=i.due_date,
                    paid_date=i.paid_date,
                    timestamp=i.timestamp,
                    primary_document_path = DocumentSelector().resolve_primary_path(documents=i.documents),
                    tags =i.tags
                )
            )

        # ⃣Mapowanie linii
        if record_lines is not None and len(record_lines) > 0:
            # for ll in invoice_lines:
            #     print(ll)
            line_exports = [
                FinancialRecordLineExport(
                    id = l.id,
                    record_reference=record_references_from_ids.get(l.financial_record_id) if l.financial_record_id else "",
                    item_name = l.item_name,
                    description=l.description,
                    quantity=l.quantity,
                    unit=l.unit,
                    net=l.amount.value,
                    vat_rate=l.amount.vat_rate,
                    tax_treatment=l.amount.tax_treatment,
                    contract_id=l.contract_id,
                    contract_node_id=l.contract_node_id,
                    value_type_id=l.value_type_id,
                )
                for l in record_lines
            ]
        else:
            line_exports = []

        bundle = FinancialRecordAssignmentExportBundle(
            records=records_exports,
            record_lines=line_exports,
            buyers=buyers,
            sellers=sellers,
            contracts=contracts,
            cost_nodes=cost_nodes,
            cost_types=cost_types,
        )


        return bundle

        # self._exporter.export(bundle,output_path=output_path)
