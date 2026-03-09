from dataclasses import dataclass
from uuid import UUID

from contract_costs.services.financial_records.assigment.ingest.dto.invoice_assignment_facts import \
    FinancialRecordAssignmentFacts
from contract_costs.services.financial_records.assigment.ingest.dto.invoice_ref_result import FinancialRecordRefResult


@dataclass
class IngestResult:
    ref_map: dict[str, FinancialRecordRefResult]
    assignment_facts: dict[UUID, FinancialRecordAssignmentFacts]