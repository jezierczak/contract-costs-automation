from dataclasses import replace
import logging
from datetime import datetime
from typing import Callable

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.common.time import utc_now
from contract_costs.model.company import CompanyType
from contract_costs.model.contract import ContractType
from contract_costs.model.financial_record import FinancialRecordStatus, FinancialRecord
from contract_costs.services.documents.document_selector import DocumentSelector
from contract_costs.services.financial_records.assigment.apply.commands.invoice_command import InvoiceCommand

from contract_costs.services.financial_records.assigment.prepare.dto.assignment_export_bundle import (
    FinancialRecordAssignmentExportBundle,
)
from contract_costs.services.financial_records.assigment.prepare.dto.generatr_financial_redcord_assignment_bundle_command import \
    GenerateFinancialRecordAssignmentBundleCommand
from contract_costs.services.financial_records.assigment.prepare.dto.invoice_export import FinancialRecordExport
from contract_costs.services.financial_records.assigment.prepare.dto.invoice_line_export import FinancialRecordLineExport
from contract_costs.services.financial_records.assigment.prepare.dto.company_export import CompanyExport
from contract_costs.services.financial_records.assigment.prepare.dto.contract_export import ContractExport
from contract_costs.services.financial_records.assigment.prepare.dto.cost_node_export import ContractNodeExport
from contract_costs.services.financial_records.assigment.prepare.dto.cost_type_export import ValueTypeExport
from contract_costs.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)


class GenerateFinancialRecordAssignmentBundleService(
    ActionHandler[GenerateFinancialRecordAssignmentBundleCommand,
                  FinancialRecordAssignmentExportBundle]
):

    def __init__(
        self,
        clock: Callable[[], datetime] = utc_now,
        # exporter: InvoiceAssignmentExporter,
    ) -> None:
        self._clock = clock
        # self._exporter = exporter

    def execute(
            self,
            *,
            action: GenerateFinancialRecordAssignmentBundleCommand,
            uow: UnitOfWork,
    ) -> FinancialRecordAssignmentExportBundle:
        record_repo = uow.financial_records
        record_line_repo = uow.financial_record_lines
        company_repo = uow.companies
        contract_repo = uow.contracts
        contract_node_repo = uow.contract_nodes
        value_type_repo = uow.value_types
        #  Dane główne

        # invoice_status = InvoiceStatus(status)
        financial_records: list[FinancialRecord] = record_repo.get_for_assignment(
            organization_id=action.organization_id,
            status=action.invoice_status)

        record_ids = [i.id for i in financial_records]

        record_references_from_ids = {i.id:i.reference for i in financial_records}

        updated_records: list[FinancialRecord] = []

        for record in financial_records:
            if record.status != FinancialRecordStatus.IN_PROGRESS:
                updated = replace(record,
                                  status=FinancialRecordStatus.IN_PROGRESS,
                                  updated_at = self._clock(),
                                  updated_by_user_id=action.actor_user_id
                                  )
                record_repo.update(updated)
                updated_records.append(updated)
            else:
                updated_records.append(record)

        record_lines = record_line_repo.list_by_financial_record_ids(
            organization_id=action.organization_id,
            financial_records_ids=record_ids)
        record_lines.extend(record_line_repo.list_unassigned(organization_id=action.organization_id))


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
            for c in company_repo.get_owners(organization_id=action.organization_id)
        ]

        sellers = [
            CompanyExport(
                id=c.id,
                name=c.name,
                tax_number=c.tax_number,
            )
            for c in company_repo.list_all(organization_id=action.organization_id)
            # for c in (self._company_repo.get(cid) for cid in company_sellers)
            if c is not None and c.role != CompanyType.OWN
        ]

        #  Contracts
        projects = contract_repo.list_contracts(
            organization_id=action.organization_id,
            contract_type=ContractType.PROJECT,
        )

        systems = contract_repo.list_contracts(
            organization_id=action.organization_id,
            contract_type=ContractType.SYSTEM,
        )

        contracts = projects+systems

        agreements = contract_repo.list_contracts(
            organization_id=action.organization_id,
            contract_type=ContractType.AGREEMENT,
        )

        project_contracts = [
            ContractExport(
                id=c.id,
                name=c.name,
                code=c.code,
            )
            for c in contracts
        ]

        agreements_contracts = [
            ContractExport(
                id=c.id,
                name=c.name,
                code=c.code,
            )
            for c in agreements
        ]

        all_contracts = agreements_contracts+project_contracts
        #  Cost nodes
        contract_code_by_id = {
            c.id: c.code
            for c in all_contracts
        }

        # project_contract_ids = {c.id for c in projects}
        # system_contract_ids = {c.id for c in systems}

        project_contract_nodes = []
        agreement_contract_nodes = []

        project_contract_ids = {c.id for c in contracts}
        agreement_contract_ids = {c.id for c in agreements}

        for n in contract_node_repo.list_leaf_nodes_for_active_contracts(
                organization_id=action.organization_id
        ):

            contract_code = contract_code_by_id.get(n.contract_id)
            if contract_code is None:
                raise RuntimeError(
                    f"Missing contract code for contract_id={n.contract_id}"
                )

            if n.contract_id in project_contract_ids:
                project_contract_nodes.append(
                    ContractNodeExport(
                        id=n.id,
                        contract_id=n.contract_id,
                        parent_id=n.parent_id,
                        code=n.code,
                        name=n.name,
                        budget=n.budget,
                        contract_code=contract_code,
                    )
                )

            elif n.contract_id in agreement_contract_ids:
                agreement_contract_nodes.append(
                    ContractNodeExport(
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
        value_types = [
            ValueTypeExport(
                id=ct.id,
                code=ct.code,
                name=ct.name,
            )
            for ct in value_type_repo.list_all(organization_id=action.organization_id)
        ]

        #  Mapowanie faktur
        records_exports = []
        for i in updated_records:
            buyer = company_repo.get(organization_id=action.organization_id,company_id=i.buyer_id) if i.buyer_id else None
            seller = company_repo.get(organization_id=action.organization_id,company_id=i.seller_id) if i.seller_id else None

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
        node_code_by_id = {
            n.id: n.code
            for n in project_contract_nodes + agreement_contract_nodes
        }

        value_type_code_by_id = {
            vt.id: vt.code
            for vt in value_types
        }
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
                    contract_code=contract_code_by_id.get(l.contract_id) if l.contract_id else None,
                    contract_node_code=node_code_by_id.get(l.contract_node_id) if l.contract_node_id else None,
                    value_type_code=value_type_code_by_id.get(l.value_type_id) if l.value_type_id else None,
                    agreement_code=contract_code_by_id.get(l.agreement_id) if l.agreement_id else None,
                    agreement_node_code=node_code_by_id.get(l.agreement_node_id) if l.agreement_node_id else None
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
            project_contracts=project_contracts,
            agreement_contracts=agreements_contracts,
            project_contract_nodes=project_contract_nodes,
            agreement_contract_nodes=agreement_contract_nodes,
            value_types=value_types,
        )


        return bundle

        # self._exporter.export(bundle,output_path=output_path)
