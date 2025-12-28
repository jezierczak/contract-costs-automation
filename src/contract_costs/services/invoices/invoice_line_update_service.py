from collections import defaultdict
from dataclasses import replace
from uuid import uuid4, UUID

from contract_costs.model.invoice_line import InvoiceLine
from contract_costs.repository.contract_repository import ContractRepository
from contract_costs.repository.cost_node_repository import CostNodeRepository
from contract_costs.repository.cost_type_repository import CostTypeRepository
from contract_costs.repository.invoice_line_repository import InvoiceLineRepository
from contract_costs.services.invoices.dto.apply import InvoiceRefResult, InvoiceApplyAction
from contract_costs.services.invoices.dto.common import InvoiceLineUpdate

from contract_costs.services.common.resolve_utils import resolve_or_none
import logging


logger = logging.getLogger(__name__)


class InvoiceLineUpdateService:
    """
    Odpowiada za:
    - tworzenie linii faktur
    - aktualizację linii faktur
    - koszty bez faktury
    """

    def __init__(self,
                 invoice_line_repository: InvoiceLineRepository,
                 contract_repository: ContractRepository,
                cost_node_repository: CostNodeRepository,
                cost_type_repository: CostTypeRepository
                 ) -> None:

        self._invoice_line_repository = invoice_line_repository
        self._contract_repository = contract_repository
        self._cost_node_repository = cost_node_repository
        self._cost_type_repository = cost_type_repository

    def apply(
        self,
        lines: list[InvoiceLineUpdate],
        ref_map: dict[str, InvoiceRefResult],
    ) ->  set[UUID]:

        invoice_line_states: dict[UUID, list[bool]] = defaultdict(list)

        invoice_lines_ids_updated: defaultdict[UUID,list[UUID]] = defaultdict(list) #fist is invoice id, second updated invoice_line_ids,

        invoice_ids_from_excel: set[UUID] = {
            ref.invoice_id
            for ref in ref_map.values()
            if ref.invoice_id is not None
        }

        for update in lines:

            ref_result = ref_map.get(update.invoice_number)

            resolved_invoice_id: UUID | None = (
                ref_result.invoice_id if ref_result else None
            )

            # Lines that reference an invoice which is not available in this batch
            # (e.g. PROCESSED invoices) are intentionally skipped.
            # Lines with empty invoice_id (costs without invoice) are still processed.
            if update.invoice_number is not None and resolved_invoice_id is None:
                logger.warning(
                    "Invoice reference '%s' not found for line '%s'. Line skipped.",
                    update.invoice_number,
                    update.item_name,
                )
                continue

            if ref_result and ref_result.action in {
                InvoiceApplyAction.DELETED,
                InvoiceApplyAction.SKIPPED,
            }:
                logger.info(
                    "Skipping lines for invoice %s (action=%s)",
                    update.invoice_number,
                    ref_result.action,
                )
                continue

            contract_id = resolve_or_none(
                self._contract_repository.get_by_code,
                update.contract_id,
                "Contract",
            )

            cost_node_id = resolve_or_none(
                self._cost_node_repository.get_by_code,
                update.cost_node_id,
                "CostNode",
            )

            cost_type_id = resolve_or_none(
                self._cost_type_repository.get_by_code,
                update.cost_type_id,
                "CostType",
            )


            if update.invoice_line_id is None:
                new_id = self._create_line(update, resolved_invoice_id, contract_id, cost_node_id, cost_type_id)
                invoice_lines_ids_updated[resolved_invoice_id].append(new_id)  # adding updated invoice lines ids by invoice_id
            else:
                self._update_line(update, resolved_invoice_id, contract_id, cost_node_id, cost_type_id)
                invoice_lines_ids_updated[resolved_invoice_id].append(update.invoice_line_id) #adding updated invoice lines ids by invoice_id

            if resolved_invoice_id is not None:
                invoice_line_states[resolved_invoice_id].append(
                    self._is_line_complete(update)
                )

        self._delete_items_erased_from_excel(invoice_ids_from_excel,invoice_lines_ids_updated)

        fully_assigned_invoice_ids ={
            inv_id for inv_id,states in invoice_line_states.items() if all(states)
        }

        logger.info(
            "Invoice lines processed: total=%d, invoices_affected=%d",
            len(lines),
            len(invoice_lines_ids_updated),
        )

        return fully_assigned_invoice_ids

    def _delete_items_erased_from_excel(
            self,
            invoice_ids: set[UUID],
            invoice_lines_ids_updated: dict[UUID, list[UUID]],
    ) -> None:
        for invoice_id in invoice_ids:
            keep_ids = set(invoice_lines_ids_updated.get(invoice_id, []))

            deleted = self._invoice_line_repository.delete_not_in_ids(
                invoice_id=invoice_id,
                keep_ids=keep_ids,
            )

            if not keep_ids:
                logger.warning(
                    "Deleting ALL invoice lines for invoice_id=%s "
                    "(no lines present in Excel)",
                    invoice_id,
                )
            elif deleted:
                logger.info(
                    "Deleted %s invoice lines for invoice_id=%s",
                    deleted,
                    invoice_id,
                )

    @staticmethod
    def _is_line_complete(update: InvoiceLineUpdate) -> bool:
        return (
                update.contract_id is not None and
                update.cost_node_id is not None and
                update.cost_type_id is not None
        )

    def _create_line(
        self,
        update: InvoiceLineUpdate,
        invoice_id: UUID | None,
        contract_id: UUID | None,
        cost_node_id: UUID | None,
        cost_type_id: UUID | None
    ) -> UUID:
        line = InvoiceLine(
            id=uuid4(),
            invoice_id=invoice_id,
            item_name=update.item_name,
            description=update.description,
            quantity=update.quantity,
            unit=update.unit,
            amount=update.amount,
            contract_id=contract_id,
            cost_node_id=cost_node_id,
            cost_type_id=cost_type_id,
        )

        self._invoice_line_repository.add(line)
        return line.id

    def _update_line(
        self,
        update: InvoiceLineUpdate,
        invoice_id: UUID | None,
        contract_id: UUID | None,
        cost_node_id: UUID | None,
        cost_type_id: UUID | None
    ) -> None:
        line = self._invoice_line_repository.get(update.invoice_line_id)
        if line is None:
            raise ValueError("Invoice line not found")

        updated = replace(
            line,
            invoice_id=invoice_id,  # 🔥 TU JEST RÓŻNICA
            item_name=update.item_name,
            description=update.description,
            quantity=update.quantity,
            unit=update.unit,
            amount=update.amount,
            contract_id=contract_id,
            cost_node_id=cost_node_id,
            cost_type_id=cost_type_id,
        )

        self._invoice_line_repository.update(updated)
