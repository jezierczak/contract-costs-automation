from datetime import date
from typing import TypedDict

from openpyxl.styles.builtins import total
from pydantic import BaseModel

from contract_costs.model.company import CompanyType
from contract_costs.model.invoice import InvoiceStatus, PaymentStatus

class CompanyReviewQuery(TypedDict,total=False):
    any: str
    tax_numbers: list[str] | str
    name: list[str] | str
    role: list[CompanyType] | CompanyType


class InvoiceReviewQuery(BaseModel):
    buyer_query: CompanyReviewQuery | None = None
    seller_query: CompanyReviewQuery | None = None
    statuses: list[InvoiceStatus] | None = None
    payment_statuses: list[PaymentStatus] | None = None

    from_date: date | None = None
    to_date: date | None = None

    only_ready_for_accountant: bool | None = None

    @staticmethod
    def build_company_query(**kwargs) -> CompanyReviewQuery | None:
        query: CompanyReviewQuery = {}
        allowed_keys = CompanyReviewQuery.__annotations__.keys()

        for k, v in kwargs.items():
            if v is None:
                continue
            if k not in allowed_keys:
                continue
            if k == "role" and isinstance(v, str):
                v = CompanyType(v)
            query[k] = v

        return query or None