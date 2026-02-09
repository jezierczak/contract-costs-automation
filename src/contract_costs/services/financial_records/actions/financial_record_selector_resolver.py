from uuid import UUID


from contract_costs.repository.financial_record_repository import FinancialRecordRepository
from contract_costs.services.financial_records.actions.dto.invoice_action_command import FinancialRecordSelector


class FinancialRecordSelectorResolver:

    def __init__(self, record_repo: FinancialRecordRepository) -> None:
        self._record_repo = record_repo

    def resolve(self,
                *,
                organization_id: UUID,
                selectors: list[FinancialRecordSelector]) -> list[UUID]:
        record_ids: list[UUID] = []

        for selector in selectors:
            # ==========================
            # SELECT BY ID
            # ==========================
            if selector.record_id:
                record = self._record_repo.get(
                    organization_id=organization_id,
                    record_id=selector.record_id)
                if not record:
                    raise ValueError(
                         f"FinancialRecord not found "
                        f"(org={organization_id}, id={selector.record_id})"
                    )
                record_ids.append(record.id)
                continue

            # ==========================================
            # SELECT BY REFERENCE
            # ==========================================
            if selector.record_reference:
                records = self._record_repo.get_by_reference(
                    organization_id=organization_id,
                    reference=selector.record_reference
                )
                if not records:
                    raise ValueError(
                        f"FinancialRecord not found "
                        f"(org={organization_id}, reference={selector.record_reference})"
                    )
                if len(records) > 1:
                    raise RuntimeError(
                        f"Ambiguous financial record reference "
                        f"(org={organization_id}, reference={selector.record_reference}, "
                        f"count={len(records)})"
                        f"Specify record ID (not implemented yet)."
                    )
                record_ids.append(records[0].id)
                continue

            # teoretycznie nieosiągalne przez Pydantic
            raise RuntimeError("Invalid financial record selector")

        return record_ids
