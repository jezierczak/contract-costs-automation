from dataclasses import dataclass
from datetime import date
from typing import TypedDict, cast, Any

from pydantic import BaseModel

from contract_costs.action_bus.action_type import ActionType, action_type
from contract_costs.action_bus.query import Query
from contract_costs.model.company import CompanyType
from contract_costs.model.contract import ContractType
from contract_costs.model.financial_record import FinancialRecordStatus, PaymentStatus
from contract_costs.model.value_direction import ValueDirection


class CompanyReviewQuery(TypedDict,total=False):
    id: list[str] | str
    any: str
    tax_numbers: list[str] | str
    name: list[str] | str
    role: list[CompanyType] | CompanyType

@dataclass(frozen=True,slots=True)
@action_type(ActionType.FINANCIAL_RECORD_VIEW)
class FinancialRecordReviewQuery(Query):
    buyer_query: CompanyReviewQuery | None = None
    seller_query: CompanyReviewQuery | None = None
    statuses: list[FinancialRecordStatus] | None = None
    payment_statuses: list[PaymentStatus] | None = None

    from_date: date | None = None
    to_date: date | None = None

    contract_codes: list[str] | None = None

    only_ready_for_accountant: bool | None = None
    direction: list[ValueDirection] | ValueDirection | None = None
    limit: int | None = None

    @staticmethod
    def build_company_query(**kwargs) -> CompanyReviewQuery | None:
        query: dict[str, Any] = {}
        allowed_keys = CompanyReviewQuery.__annotations__.keys()

        for k, v in kwargs.items():
            if v is None:
                continue
            if k not in allowed_keys:
                continue
            if k == "role" and isinstance(v, str):
                v = CompanyType(v)
            query[k] = v

        return cast(CompanyReviewQuery, query) if query else None