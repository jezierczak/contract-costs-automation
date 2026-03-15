from collections import defaultdict
from dataclasses import replace
from datetime import datetime
from typing import Callable
from uuid import UUID

from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now
from contract_costs.model.financial_record_line import FinancialRecordLine
from contract_costs.model.value_direction import ValueDirection
from contract_costs.repository.contract_repository import ContractRepository
from contract_costs.repository.contract_node_repository import ContractNodeRepository
from contract_costs.repository.value_type_repository import ValueTypeRepository
from contract_costs.repository.financial_record_line_repository import FinancialRecordLineRepository
from contract_costs.services.financial_records.assigment.ingest.dto.invoice_assignment_facts import FinancialRecordAssignmentFacts
from contract_costs.services.financial_records.assigment.ingest.dto.invoice_ref_result import FinancialRecordRefResult, RecordApplyAction
from contract_costs.services.financial_records.assigment.invoice_sources.dto.common import FinancialRecordLineUpdate

from contract_costs.services.common.resolve_utils import resolve_or_none
import logging

from contract_costs.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)


class FinancialRecordLineUpdateService:
    """
    Odpowiada za:
    - tworzenie linii faktur
    - aktualizację linii faktur
    - koszty bez faktury
    """

    def __init__(self,
                 id_generator: Callable[[], UUID] = new_uuid,
                 clock: Callable[[], datetime] = utc_now

                 ) -> None:
        self._id_generator = id_generator
        self._clock = clock

    def apply(
            self,
            *,
            uow:UnitOfWork,
            organization_id: UUID,
            actor_user_id: UUID,
            lines: list[FinancialRecordLineUpdate],
            ref_map: dict[str, FinancialRecordRefResult],
    ) -> dict[UUID, FinancialRecordAssignmentFacts]:
        # Excel is the source of truth for invoice-line relations.
        # If invoice_number is changed, line references MUST be updated in the batch.
        # The system does not auto-migrate invoice lines.

        record_line_repo = uow.financial_record_lines
        contract_repo = uow.contracts
        contract_node_repo = uow.contract_nodes
        value_type_repo = uow.value_types

        record_lines_updated: defaultdict[UUID,list[FinancialRecordLine]] = defaultdict(list) #fist is invoice id, second updated invoice_line_ids,

        record_ids_subject_to_cleanup: set[UUID] = {
            ref.record_id
            for ref in ref_map.values()
            if ref.record_id is not None
               and ref.action == RecordApplyAction.APPLIED
        }

        value_type_directions_map: dict[UUID, ValueDirection] = {
            value_type.id: value_type.direction for value_type in value_type_repo.list_all(
                organization_id=organization_id)
        }

        for update in lines:
            if update.record_reference:
                # ref_result = ref_map.get(update.invoice_number)
                ref_result = self._resolve_ref(update, ref_map)
            else: ref_result = None

            resolved_record_id: UUID | None = (
                ref_result.record_id if ref_result else None
            )

            # Lines that reference an invoice which is not available in this batch
            # (e.g. PROCESSED invoices) are intentionally skipped.
            # Lines with empty invoice_id (costs without invoice) are still processed.
            if update.record_reference is not None and resolved_record_id is None:
                logger.warning(
                    "Invoice reference '%s' not found for line '%s'. Line skipped.",
                    update.record_reference,
                    update.item_name,
                )
                continue

            if ref_result and ref_result.action in {
                RecordApplyAction.DELETED,
                RecordApplyAction.SKIPPED,
            }:
                logger.info(
                    "Skipping lines for invoice %s (action=%s)",
                    update.record_reference,
                    ref_result.action,
                )
                continue

            contract_id = resolve_or_none(
                contract_repo.get_by_code,
                organization_id,
                update.contract_reference,
                "Contract",
            )
            # logger.info(f"OrganizationID: {organization_id}, contract_code: {update.contract_node_code}")
            # contract_node_id = resolve_or_none(
            #     contract_node_repo.get_by_code,
            #     organization_id,
            #     update.contract_node_code,
            #     "ContractNode",
            # )
            contract_node_id = None
            if contract_id:
                contract_node = contract_node_repo.get_by_code(
                    organization_id=organization_id,
                    contract_id=contract_id,
                    contract_node_code=update.contract_node_reference
                )
                if contract_node:
                    contract_node_id = contract_node.id

            value_type_id = resolve_or_none(
                value_type_repo.get_by_code,
                organization_id,
                update.value_type_reference,
                "ValueType",
            )

            #TODO resolve agreement_id powinno działać trzeba to sprawdzić
            agreement_id = resolve_or_none(
                contract_repo.get_by_code,
                organization_id,
                update.agreement_reference,
                "AgreementContract",
            )

            agreement_node_id = resolve_or_none(
                contract_node_repo.get_by_code,
                organization_id,
                update.agreement_node_reference,
                "AgreementContractNode",
            )


            if resolved_record_id:
                if update.record_line_id is None:
                    new_id = self._create_line(
                        record_line_repo,
                        organization_id,
                        actor_user_id,update,
                        resolved_record_id,
                        contract_id,
                        contract_node_id,
                        value_type_id,
                        agreement_id,
                        agreement_node_id
                    )
                    line = record_line_repo.get(
                        organization_id=organization_id,
                        line_id=new_id)
                    if line is None:
                        raise RuntimeError(f"InvoiceLine not found after create: {new_id}")
                    record_lines_updated[resolved_record_id].append(line)  # adding updated invoice lines ids by invoice_id
                else:
                    self._update_line(
                        record_line_repo,
                        organization_id,
                        actor_user_id,
                        update,
                        resolved_record_id,
                        contract_id,
                        contract_node_id,
                        value_type_id,
                        agreement_id,
                        agreement_node_id
                    )
                    line = record_line_repo.get(
                        organization_id=organization_id,
                        line_id=update.record_line_id)
                    if line is None:
                        raise RuntimeError(f"InvoiceLine not found: {update.record_line_id}")

                    record_lines_updated[resolved_record_id].append(line) #adding updated invoice lines ids by invoice_id

                # if resolved_invoice_id is not None:
                #     invoice_line_states[resolved_invoice_id].append(
                #         self._is_line_complete(update)
                #     )
                #     if value_type_id is not None:
                #         value_type = self._value_type_repository.get(value_type_id)
                #         if value_type:
                #             invoice_lines_directions[resolved_invoice_id].add(value_type.direction)
        record_lines_ids_updated: dict[UUID, list[UUID]] = {}
        for rec_id, lines_up in record_lines_updated.items():
            record_lines_ids_updated[rec_id] = [line_up.id for line_up in lines_up]

        self._delete_items_erased_from_excel(record_line_repo,organization_id,record_ids_subject_to_cleanup,record_lines_ids_updated)

        logger.info(
            "Financial record lines processed: total=%d, invoices_affected=%d",
            len(lines),
            len(record_lines_ids_updated),
        )

        record_assignment_facts: dict[UUID, FinancialRecordAssignmentFacts] = {}

        for ref in ref_map.values():
            if not ref.record_id:
                continue
            if ref.action != RecordApplyAction.APPLIED:
                continue

            # states = invoice_line_states.get(ref.invoice_id, [])
            # directions = invoice_lines_directions.get(ref.invoice_id, set())

            record_assignment_facts[ref.record_id] = FinancialRecordAssignmentFacts(
                record_id=ref.record_id,
                invoice_lines=record_lines_updated[ref.record_id],
                buyer_role=ref.buyer_role,
                seller_role=ref.seller_role,
                value_type_directions_map=value_type_directions_map
            )

        return record_assignment_facts

    def _delete_items_erased_from_excel(
            self,
            record_line_repo,
            organization_id: UUID,
            record_ids: set[UUID],
            record_lines_ids_updated: dict[UUID, list[UUID]],
    ) -> None:
        for record_id in record_ids:

            if record_id not in record_lines_ids_updated:
                logger.debug(
                    "Skipping cleanup for invoice_id=%s (no lines updated in batch)",
                    record_id,
                )
                continue

            keep_ids = set(record_lines_ids_updated.get(record_id, []))

            deleted = record_line_repo.delete_not_in_ids(
                organization_id=organization_id,
                financial_record_id=record_id,
                keep_ids=keep_ids,
            )

            if not keep_ids:
                logger.warning(
                    "Deleting ALL invoice lines for invoice_id=%s "
                    "(no lines present in Excel)",
                    record_id,
                )
            elif deleted:
                logger.info(
                    "Deleted %s invoice lines for invoice_id=%s",
                    deleted,
                    record_id,
                )


    def _create_line(
        self,
        record_line_repo: FinancialRecordLineRepository,
        organization_id: UUID,
        actor_user_id: UUID,
        update: FinancialRecordLineUpdate,
        record_id: UUID | None,
        contract_id: UUID | None,
        cost_node_id: UUID | None,
        cost_type_id: UUID | None,
        agreement_id: UUID | None,
        agreement_node_id: UUID | None,

    ) -> UUID:

        line = FinancialRecordLine(
            id=self._id_generator(),
            organization_id=organization_id,
            financial_record_id=record_id,
            item_name=update.item_name,
            description=update.description,
            quantity=update.quantity,
            unit=update.unit,
            amount=update.amount,
            contract_id=contract_id,
            contract_node_id=cost_node_id,
            value_type_id=cost_type_id,
            created_at=self._clock(),
            created_by_user_id=actor_user_id,
            updated_at=None,
            updated_by_user_id=None,
            agreement_id = agreement_id,
            agreement_node_id = agreement_node_id
        )

        record_line_repo.add(organization_id=organization_id,line=line)
        return line.id

    def _update_line(
        self,
        record_line_repo: FinancialRecordLineRepository,
        organization_id: UUID,
        actor_user_id: UUID,
        update: FinancialRecordLineUpdate,
        record_id: UUID | None,
        contract_id: UUID | None,
        contract_node_id: UUID | None,
        value_type_id: UUID | None,
        agreement_id: UUID | None,
        agreement_node_id: UUID | None,

    ) -> None:
        if update.record_line_id:
            line = record_line_repo.get(organization_id=organization_id,line_id=update.record_line_id)
            if line is None:
                raise ValueError("Invoice line not found")
        else: raise ValueError("Invoice line not found")

        updated = replace(
            line,
            financial_record_id=record_id,  # 🔥 TU JEST RÓŻNICA
            item_name=update.item_name,
            description=update.description,
            quantity=update.quantity,
            unit=update.unit,
            amount=update.amount,
            contract_id=contract_id,
            contract_node_id=contract_node_id,
            value_type_id=value_type_id,
            updated_by_user_id=actor_user_id,
            updated_at=self._clock(),
            agreement_id=agreement_id,
            agreement_node_id=agreement_node_id

        )

        record_line_repo.update(organization_id=organization_id,line=updated)

    @staticmethod
    def _resolve_ref(
            update: FinancialRecordLineUpdate,
            ref_map: dict[str, FinancialRecordRefResult],
    ) -> FinancialRecordRefResult | None:

        # 1️⃣ normalne dopasowanie (nowy numer)
        if update.record_reference in ref_map:
            return ref_map[update.record_reference]

        # 2️⃣ dopasowanie przez old_invoice_number
        for ref in ref_map.values():
            if ref.old_record_reference == update.record_reference:
                return ref

        return None