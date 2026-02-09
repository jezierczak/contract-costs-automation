import logging
from datetime import date
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import Any, Type, TypeVar
from uuid import uuid4

from contract_costs.model.amount import Amount, VatRate
from contract_costs.model.company import CompanyType
from contract_costs.model.document import DocumentType
from contract_costs.model.financial_record import (
    FinancialRecordStatus,
    PaymentMethod,
    PaymentStatus,
)
from contract_costs.model.unit_of_measure import UnitOfMeasure
from contract_costs.services.common.resolve_utils import normalize_tax_number
from contract_costs.services.financial_records.assigment.apply.commands.invoice_command import (
    InvoiceCommand,
)
from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.dto.parse import (
    DocumentParseResult,
    FinancialRecordUpdate,
    FinancialRecordLineUpdate,
    CompanyInput,
)

logger = logging.getLogger(__name__)

E = TypeVar("E", bound=Enum)


class AIDocumentMapper:
    """
    Mapuje surowe dane AI → DTO.
    ZERO logiki domenowej.
    ZERO decyzji biznesowych.
    """

    def map(self, data: dict[str, Any]) -> DocumentParseResult:
        # ------------------------
        # DOCUMENT TYPE
        # ------------------------
        raw_doc_type = data.get("document_type")
        document_type = self._parse_enum(DocumentType, raw_doc_type) or DocumentType.UNKNOWN

        # ------------------------
        # INVOICE NUMBER
        # ------------------------
        raw_invoice_number = data.get("invoice_number")

        invoice_number = (
            str(raw_invoice_number).strip()
            if raw_invoice_number and str(raw_invoice_number).strip()
            else f"AI-{uuid4().hex[:12]}"
        )

        if raw_invoice_number is None:
            logger.warning(
                "Invoice number missing from AI, generated technical number: %s",
                invoice_number,
            )

        # ------------------------
        # PAYMENT
        # ------------------------
        payment_method = (
            self._parse_enum(PaymentMethod, data.get("payment_method"))
            or PaymentMethod.UNKNOWN
        )

        payment_status = (
            self._parse_enum(PaymentStatus, data.get("payment_status"))
            or PaymentStatus.UNKNOWN
        )

        # ------------------------
        # RECORD DTO (neutral)
        # ------------------------
        record = FinancialRecordUpdate(
            command=InvoiceCommand.APPLY,
            old_reference=None,
            record_id=None,
            reference=invoice_number,
            invoice_date=self._parse_date(data.get("invoice_date")),
            selling_date=self._parse_date(data.get("selling_date")),
            due_date=self._parse_date(data.get("due_date")),
            paid_date=self._parse_date(data.get("paid_date")),
            buyer_tax_number=None,
            seller_tax_number=None,
            payment_method=payment_method,
            payment_status=payment_status,
            status=FinancialRecordStatus.DRAFT,  # 🔥 neutral
            # scan_filename=None,
            tags=None,
        )

        # ------------------------
        # LINES
        # ------------------------
        lines: list[FinancialRecordLineUpdate] = []

        for item in data.get("invoice_items", []) or []:
            quantity = self._parse_decimal(item.get("quantity"))
            net_total = self._parse_decimal(item.get("net_total"))
            vat_rate = self._parse_vat(item.get("vat_rate"))
            unit = self._parse_enum(UnitOfMeasure, item.get("unit")) or UnitOfMeasure.UNKNOWN

            lines.append(
                FinancialRecordLineUpdate(
                    record_line_id=None,
                    record_reference=None,
                    item_name=item.get("item_name") or "-----",
                    description=item.get("description"),
                    quantity=quantity,
                    unit=unit,
                    amount=Amount(
                        value=net_total,
                        vat_rate=vat_rate,
                    ),
                    contract_id=None,
                    contract_node_id=None,
                    value_type_code=None,
                )
            )

        # ------------------------
        # COMPANIES
        # ------------------------
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

        # ------------------------
        # RETURN DTO
        # ------------------------
        return DocumentParseResult(
            document_type=document_type,
            record=record,
            lines=lines,
            buyer=buyer,
            seller=seller,
        )

    # ============================================================
    # SAFE PARSERS
    # ============================================================

    @staticmethod
    def _parse_date(value: str | None) -> date | None:
        if not value:
            return None
        try:
            return date.fromisoformat(value)
        except Exception:
            logger.warning("Invalid date from AI: %s", value)
            return None

    @staticmethod
    def _parse_decimal(value: Any) -> Decimal:
        if value is None:
            return Decimal("0")

        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError):
            logger.warning("Invalid decimal from AI: %s", value)
            return Decimal("0")

    @staticmethod
    def _parse_enum(enum_cls: Type[E], value: str | None) -> E | None:
        if not value:
            return None
        try:
            return enum_cls(value)
        except Exception:
            logger.warning("Invalid %s from AI: %s", enum_cls.__name__, value)
            return None

    @staticmethod
    def _parse_vat(value: str | None) -> VatRate:
        if not value:
            return VatRate.VAT_23

        try:
            return VatRate(f"VAT_{value}")
        except Exception:
            logger.warning("Invalid VAT rate from AI: %s", value)
            return VatRate.VAT_23
