import logging
import re
from datetime import date
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import Any, Type, TypeVar
from uuid import uuid4

from contract_costs.model.amount import Amount, VatRate, AmountInputType
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

UNIT_ALIASES = {
        "szt": "PIECE",
        "szt.": "PIECE",
        "sztuk": "PIECE",

        "m": "METER",
        "mb": "METER",

        "m2": "SQUARE_METER",
        "m²": "SQUARE_METER",

        "m3": "CUBIC_METER",
        "m³": "CUBIC_METER",

        "kg": "KILOGRAM",
        "t": "TON",

        "h": "HOUR",
        "godz": "HOUR",
        "godzina": "HOUR",

        "day": "DAY",
        "dzien": "DAY",

        "usluga": "SERVICE",
        "usługa": "SERVICE",
        "services": "SERVICE",

        "l": "LITER",
    }

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
            unit = self._parse_unit(item.get("unit")) or UnitOfMeasure.UNKNOWN

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
                        input_type=AmountInputType.NET
                    ),
                    contract_reference=None,
                    contract_node_reference=None,
                    value_type_reference=None,
                    agreement_reference=None,
                    agreement_node_reference=None
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

        raw = str(value).strip()

        if not raw:
            return Decimal("0")

        try:
            # usuń spacje (1 234,56 → 1234,56)
            raw = raw.replace(" ", "")

            # przypadek: 1,234.56 (US)
            if "," in raw and "." in raw:
                if raw.rfind(",") < raw.rfind("."):
                    # przecinek = separator tysięcy
                    raw = raw.replace(",", "")
                else:
                    # kropka = separator tysięcy
                    raw = raw.replace(".", "").replace(",", ".")
            # przypadek: tylko przecinek → separator dziesiętny
            elif "," in raw:
                raw = raw.replace(",", ".")

            return Decimal(raw)

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
    def _parse_unit(value: str | None) -> UnitOfMeasure:
        if not value:
            return UnitOfMeasure.UNKNOWN

        raw = value.strip().lower()

        # alias
        if raw in UNIT_ALIASES:
            return UnitOfMeasure[UNIT_ALIASES[raw]]

        # próba po value enum
        for unit in UnitOfMeasure:
            if unit.value == raw:
                return unit

        logger.warning("Invalid UnitOfMeasure from AI: %s", value)
        return UnitOfMeasure.UNKNOWN


    @staticmethod
    def _parse_vat(value: str | None) -> VatRate:
        if not value:
            return VatRate.VAT_23

        raw = str(value).strip().lower().replace(",", ".")

        # zwolnione
        if raw in {"zw", "zw.", "zwolnione"}:
            return VatRate.VAT_ZW

        # usuwamy %
        raw = raw.replace("%", "")

        # jeżeli ktoś podał 0.23 zamiast 23
        try:
            decimal_val = Decimal(raw)
            if decimal_val <= 1:
                percent = int(decimal_val * 100)
            else:
                percent = int(decimal_val)
        except Exception:
            match = re.search(r"\d+", raw)
            if not match:
                logger.warning("Invalid VAT rate from AI: %s", value)
                return VatRate.VAT_23
            percent = int(match.group())

        try:
            return VatRate[f"VAT_{percent}"]
        except KeyError:
            logger.warning("Invalid VAT rate from AI: %s", value)
            return VatRate.VAT_23