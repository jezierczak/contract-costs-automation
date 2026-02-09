from dataclasses import dataclass
from datetime import date
from uuid import UUID


@dataclass(frozen=True)
class CandidateRecordDto:
    record_id: UUID
    reference: str | None
    status: str
    invoice_date: date | None
