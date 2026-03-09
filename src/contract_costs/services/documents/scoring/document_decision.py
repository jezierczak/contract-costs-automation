from enum import Enum

from dataclasses import dataclass
from uuid import UUID
from typing import Optional


class DocumentDecision(Enum):
    AUTO_ATTACH = "auto_attach"
    AUTO_CREATE = "auto_create"
    MANUAL = "manual"


@dataclass(frozen=True, slots=True)
class DocumentDecisionResult:
    decision: DocumentDecision
    record_id: Optional[UUID] = None
