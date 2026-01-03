import logging
from datetime import date
from decimal import Decimal
from typing import Any
from uuid import uuid4

from contract_costs.model.company import CompanyType
from contract_costs.model.unit_of_measure import UnitOfMeasure
from contract_costs.services.common.resolve_utils import normalize_tax_number
from contract_costs.services.invoices.commands.invoice_command import InvoiceCommand
from contract_costs.services.invoices.dto.parse import (
    InvoiceParseResult,
    InvoiceUpdate,
    InvoiceLineUpdate,
    CompanyInput,
)
from contract_costs.model.amount import Amount, VatRate
from contract_costs.model.invoice import InvoiceStatus, PaymentMethod, PaymentStatus

logger = logging.getLogger(__name__)

class AIInvoiceMapper:
    """
    Mapuje surowe dane AI → DTO.
    NIE zawiera logiki domenowej.
    """

    def map(self, data: dict[str, Any]) -> InvoiceParseResult:
        raw_invoice_number = data.get("invoice_number")

        invoice_number = (
            raw_invoice_number
            if raw_invoice_number and str(raw_invoice_number).strip()
            else f"AI-{uuid4().hex[:12]}"
        )

        if raw_invoice_number is None:
            logger.warning(
                "Invoice number not provided by AI, generated technical number: %s",
                invoice_number,
            )

        invoice = InvoiceUpdate(
            command=InvoiceCommand.APPLY,
            old_invoice_number=None,
            invoice_number=invoice_number,
            invoice_date=self.parse_date(data.get("invoice_date")),
            selling_date=self.parse_date(data.get("selling_date")),
            due_date=self.parse_date(data.get("due_date")),
            buyer_tax_number=None,
            seller_tax_number=None,
            payment_method=self.parse_enum(PaymentMethod,data.get("payment_method")) or PaymentMethod.UNKNOWN,
            payment_status=self.parse_enum(PaymentStatus,data.get("payment_status")) or PaymentStatus.UNKNOWN,
            status=InvoiceStatus.NEW,
        )

        lines = [
            InvoiceLineUpdate(
                invoice_line_id=None,
                invoice_number=None,
                item_name=item.get("item_name") or "-----",
                description=item.get("description"),
                quantity=item.get("quantity") or Decimal("0"),
                unit=item.get("unit") or UnitOfMeasure.UNKNOWN,
                amount=Amount(
                    value=item.get("net_total") or Decimal("0"),
                    vat_rate=item.get("vat_rate") or VatRate.VAT_23,
                ),
                contract_id=None,
                cost_node_id=None,
                cost_type_id=None,
            )
            for item in data.get("invoice_items", [])
        ]

        buyer = CompanyInput(
            name=data.get("buyer_name"),
            tax_number=normalize_tax_number(data.get("buyer_tax_number")),
            street=data.get("buyer_street"),
            city=data.get("buyer_city"),
            state=data.get("buyer_state"),
            zip_code=data.get("buyer_zip_code"),
            country=data.get("buyer_country"),
            phone_number=data.get("buyer_phone_number"),
            email=data.get("buyer_email"),
            bank_account=data.get("buyer_bank_account"),
            role=CompanyType.BUYER.value,
        )

        seller = CompanyInput(
            name=data.get("seller_name"),
            tax_number=normalize_tax_number(data.get("seller_tax_number")),
            street=data.get("seller_street"),
            city=data.get("seller_city"),
            state=data.get("seller_state"),
            zip_code=data.get("seller_zip_code"),
            country=data.get("seller_country"),
            phone_number=data.get("seller_phone_number"),
            email=data.get("seller_email"),
            bank_account=data.get("seller_bank_account"),
            role=CompanyType.SELLER.value,
        )

        return InvoiceParseResult(
            invoice=invoice,
            lines=lines,
            buyer=buyer,
            seller=seller,
        )
    @staticmethod
    def parse_date(value: str | None) -> date | None:
        if not value:
            return None
        try:
            return date.fromisoformat(value)
        except ValueError:
            logger.warning("Invalid date from AI: %s", value)
            return None
    @staticmethod
    def parse_enum(enum_cls, value: str | None):
        if not value:
            return None
        try:
            return enum_cls(value)
        except ValueError:
            logger.warning("Invalid %s: %s", enum_cls.__name__, value)
            return None