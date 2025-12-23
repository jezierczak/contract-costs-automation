from collections import defaultdict
from dataclasses import replace
from uuid import uuid4, UUID

from contract_costs.model.invoice_line import InvoiceLine
from contract_costs.repository.contract_repository import ContractRepository
from contract_costs.repository.cost_node_repository import CostNodeRepository
from contract_costs.repository.cost_type_repository import CostTypeRepository
from contract_costs.repository.invoice_line_repository import InvoiceLineRepository
from contract_costs.services.invoices.dto.common import InvoiceLineUpdate

from contract_costs.services.common.resolve_utils import resolve_or_none


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
        ref_map: dict[str, UUID],
    ) ->  set[UUID]:

        invoice_line_states: dict[UUID, list[bool]] = defaultdict(list)
        # print("********************************************1")
        for update in lines:

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

            invoice_id = ref_map.get(update.invoice_id)
            if update.invoice_id is not None and invoice_id is None:
                raise ValueError(
                    f"Invoice reference not found for line: {update.invoice_id}"
                )

            if update.invoice_line_id is None:
                self._create_line(update, invoice_id, contract_id, cost_node_id, cost_type_id)
            else:
                self._update_line(update, invoice_id, contract_id, cost_node_id, cost_type_id)

            if invoice_id is not None:
                invoice_line_states[invoice_id].append(
                    self._is_line_complete(update)
                )


        fully_assigned_invoice_ids ={
            inv_id for inv_id,states in invoice_line_states.items() if all(states)
        }

        return fully_assigned_invoice_ids

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
    ) -> None:
        line = InvoiceLine(
            id=uuid4(),
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
        # print("ADDING LINE")
        # print(line)
        self._invoice_line_repository.add(line)

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

    # @staticmethod
    # def _resolve_invoice_id(
    #     ref: InvoiceRef | None,
    #     ref_map: dict[str, UUID],
    # ) -> UUID | None:
    #     """
    #     Rozwiązuje invoice_id na podstawie:
    #     - None → koszt bez faktury
    #     - invoice_id → istniejąca faktura
    #     - external_ref → nowa faktura z Excela
    #     """
    #     if ref is None:
    #         return None
    #
    #     if ref.invoice_id is not None:
    #         return ref.invoice_id
    #
    #     if ref.external_ref is not None:
    #         if ref.external_ref not in ref_map:
    #             raise ValueError(
    #                 f"Invoice external_ref not found: {ref.external_ref}"
    #             )
    #         return ref_map[ref.external_ref]
    #
    #     raise ValueError("Invalid InvoiceRef")
