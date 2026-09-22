from dataclasses import replace
from decimal import Decimal, InvalidOperation
from datetime import date
from typing import Any
from uuid import uuid4

from contract_costs.model.company import CompanyType
from contract_costs.model.document import DocumentType
from contract_costs.services.financial_records.assigment.apply.commands.invoice_command import InvoiceCommand
from contract_costs.services.financial_records.assigment.invoice_sources.dto.common import FinancialRecordUpdate, \
    FinancialRecordLineUpdate
from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.dto.parse import \
    DocumentParseResult, CompanyInput
from contract_costs.model.amount import VatRate, Amount, TaxTreatment, AmountInputType
from contract_costs.model.unit_of_measure import UnitOfMeasure
from contract_costs.model.financial_record import (
    PaymentMethod,
    PaymentStatus,
    FinancialRecordStatus,
)

def _safe_decimal(value, default: Decimal) -> Decimal:
    try:
        return Decimal(str(value).replace(",", "."))
    except (InvalidOperation, TypeError):
        return default


def _safe_date(value) -> date | None:
    if not value:
        return None
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


class DocumentParseNormalizer:
    """
    Domenowy normalizator danych z parsera.
    Zapewnia spójność i akceptowalność przez DB.
    """

    def normalize_payload(self, payload: dict) -> DocumentParseResult:
        payload_data = payload if isinstance(payload, dict) else {}
        record_data = self._as_dict(payload_data.get("record"))
        buyer_data = self._as_dict(payload_data.get("buyer"))
        seller_data = self._as_dict(payload_data.get("seller"))
        lines_data = payload_data.get("lines", [])
        if not isinstance(lines_data, list):
            lines_data = []

        record = self._build_record_update(record_data)
        lines = [
            self._build_line_update(line)
            for line in lines_data
            if isinstance(line, dict)
        ]

        return DocumentParseResult(
            document_type=self._resolve_document_type(payload_data.get("document_type")),
            record=record,
            lines=lines,
            buyer=self._build_company_input(
                buyer_data,
                default_role=CompanyType.BUYER,
            ),
            seller=self._build_company_input(
                seller_data,
                default_role=CompanyType.SELLER,
            ),
        )

    # def normalize(self, payload: dict) -> DocumentParseResult:
    #     record_data = payload.get("record", {})
    #     buyer_data = payload.get("buyer", {})
    #     seller_data = payload.get("seller", {})
    #     lines_data = payload.get("lines", [])
    #     record = self._normalize_record(parsed.record)
    #     lines = [self._normalize_line(l) for l in parsed.lines]
    #
    #     return DocumentParseResult(
    #         record=record,
    #         lines=lines,
    #         buyer=parsed.buyer,
    #         seller=parsed.seller,
    #     )
    @staticmethod
    def _normalize_record(record):
        invoice_date = _safe_date(record.invoice_date)
        selling_date = _safe_date(record.selling_date) or invoice_date
        due_date = _safe_date(record.due_date)
        paid_date = _safe_date(record.paid_date)

        return replace(
            record,
            invoice_date=invoice_date,
            selling_date=selling_date,
            due_date=due_date,
            paid_date=paid_date,
            # payment_method=invoice.payment_method,
            # payment_status=self._payment_status(invoice.payment_status),
            status=record.status or FinancialRecordStatus.NEW_COST,
        )

    def _normalize_line(self, line):
        quantity = _safe_decimal(line.quantity, Decimal("1"))
        value = _safe_decimal(line.amount.value, Decimal("0.00"))

        return replace(
            line,
            quantity=quantity,
            unit=self._unit(line.unit),
            amount=replace(
                line.amount,
                value=value,
                vat_rate=self._parse_vat(line.amount.vat_rate),
            ),
        )
    @staticmethod
    def _unit( value) -> UnitOfMeasure:
        return {
            "szt": UnitOfMeasure.PIECE,
            "pcs": UnitOfMeasure.PIECE,
            "kg": UnitOfMeasure.KILOGRAM,
            "m": UnitOfMeasure.METER,
            "m2": UnitOfMeasure.SQUARE_METER,
            "m3": UnitOfMeasure.CUBIC_METER,
            "h": UnitOfMeasure.HOUR,
        }.get(str(value).lower(), UnitOfMeasure.PIECE)

    # @staticmethod
    # def _vat_rate(value) -> VatRate:
    #     return {
    #         "23": VatRate.VAT_23,
    #         "8": VatRate.VAT_8,
    #         "5": VatRate.VAT_5,
    #         "0": VatRate.VAT_0,
    #         "zw": VatRate.VAT_ZW,
    #         "oo": VatRate.VAT_ZW,
    #         "np": VatRate.VAT_ZW,
    #     }.get(str(value).lower(), VatRate.VAT_ZW)

    @staticmethod
    def _parse_vat(value: str | None) -> VatRate:
        if not value:
            return VatRate.VAT_23

        try:
            return VatRate(Decimal(str(value)))
        except Exception:
            return VatRate.VAT_23

    def _build_record_update(self, data: dict[str,Any]) -> FinancialRecordUpdate:
        reference = str(data.get("reference") or "").strip()
        if not reference:
            reference = f"AI-{uuid4().hex[:12]}"

        return FinancialRecordUpdate(
            command=InvoiceCommand.APPLY,

            reference=reference,
            record_id=None,
            old_reference=data.get("old_reference"),

            invoice_date=_safe_date(data.get("invoice_date")),
            selling_date=_safe_date(data.get("selling_date")),

            buyer_tax_number=data.get("buyer_tax_number"),
            seller_tax_number=data.get("seller_tax_number"),

            payment_method=self._payment_method(data.get("payment_method")),
            due_date=_safe_date(data.get("due_date")),
            paid_date=_safe_date(data.get("paid_date")),

            # scan_filename=data.get("scan_filename"),
            tags=None,

            payment_status=self._payment_status(data.get("payment_status")),
            status=FinancialRecordStatus.NEW_COST,
        )

    def _build_line_update(self, data: dict[str,Any]) -> FinancialRecordLineUpdate:
        amount_data = data.get("amount", {})
        if not isinstance(amount_data, dict):
            amount_data = {}

        return FinancialRecordLineUpdate(
            record_line_id=None,
            record_reference=None,

            item_name=str(data.get("item_name") or "").strip(),
            description=str(data.get("description") or "").strip(),

            quantity=_safe_decimal(data.get("quantity"), Decimal("1")),
            unit=self._unit(data.get("unit")),

            amount=Amount(
                value=_safe_decimal(amount_data.get("value"), Decimal("0.00")),
                vat_rate=self._parse_vat(amount_data.get("vat_rate")),
                tax_treatment=TaxTreatment.TAX_DEDUCTIBLE,
                input_type=self._parse_input_type(amount_data.get("input_type")),
            ),

            contract_reference=data.get("contract_code"),
            contract_node_reference=data.get("contract_node_code"),
            value_type_reference=data.get("value_type_code"),
            agreement_reference=data.get("agreement_code"),
            agreement_node_reference=data.get("agreement_node_code"),

        )

    @staticmethod
    def _parse_input_type(value) -> AmountInputType:
        # Pipeline AI zawsze ekstrahuje kwoty netto (patrz ai_invoice_mapper.py),
        # a starsze zapisane payloady (sprzed dodania tego pola) go w ogóle nie mają –
        # NET jest bezpiecznym domyślnym fallbackiem, nie zgadywaniem.
        if not value:
            return AmountInputType.NET

        try:
            return AmountInputType(str(value).lower())
        except Exception:
            raise ValueError(f"Invalid input_type: {value}")

    @staticmethod
    def _build_company_input(
        data: dict[str,Any],
        *,
        default_role: CompanyType,
    ) -> CompanyInput:
        role = str(data.get("role") or "").strip()
        if role not in {company_type.value for company_type in CompanyType}:
            role = default_role.value

        return CompanyInput(
            name=data.get("name"),
            tax_number=data.get("tax_number"),
            street=data.get("street"),
            city=data.get("city"),
            state=data.get("state"),
            zip_code=data.get("zip_code"),
            country=data.get("country"),
            phone_number=data.get("phone_number"),
            email=data.get("email"),
            bank_account=data.get("bank_account"),
            role=role,
        )

    @staticmethod
    def _as_dict(value: Any) -> dict[str, Any]:
        return value if isinstance(value, dict) else {}

    @staticmethod
    def _payment_method(value) -> PaymentMethod:
        return {
            "bank_transfer": PaymentMethod.BANK_TRANSFER,
            "cash": PaymentMethod.CASH,
            "card": PaymentMethod.CARD,
            "blik": PaymentMethod.BLIK,
            "bon": PaymentMethod.BON,
            "check": PaymentMethod.CHECK,
            "credit": PaymentMethod.CREDIT,
        }.get(str(value).lower(), PaymentMethod.UNKNOWN)

    @staticmethod
    def _payment_status(value) -> PaymentStatus:
        return {
            "paid": PaymentStatus.PAID,
            "unpaid": PaymentStatus.UNPAID,
            "partially_paid": PaymentStatus.PARTIALLY_PAID,
        }.get(str(value).lower(), PaymentStatus.UNKNOWN)

    @staticmethod
    def _resolve_document_type(value) -> DocumentType:
        try:
            return DocumentType(value)
        except Exception:
            return DocumentType.INVOICE
