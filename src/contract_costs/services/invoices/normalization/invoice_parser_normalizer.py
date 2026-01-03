from dataclasses import replace
from decimal import Decimal, InvalidOperation
from datetime import date

from contract_costs.services.invoices.dto.parse import InvoiceParseResult
from contract_costs.model.amount import Amount, VatRate
from contract_costs.model.unit_of_measure import UnitOfMeasure
from contract_costs.model.invoice import (
    PaymentMethod,
    PaymentStatus,
    InvoiceStatus,
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


class InvoiceParseNormalizer:
    """
    Domenowy normalizator danych z parsera.
    Zapewnia spójność i akceptowalność przez DB.
    """

    def normalize(self, parsed: InvoiceParseResult) -> InvoiceParseResult:
        invoice = self._normalize_invoice(parsed.invoice)
        lines = [self._normalize_line(l) for l in parsed.lines]

        return InvoiceParseResult(
            invoice=invoice,
            lines=lines,
            buyer=parsed.buyer,
            seller=parsed.seller,
        )

    def _normalize_invoice(self, invoice):
        invoice_date = _safe_date(invoice.invoice_date)
        selling_date = _safe_date(invoice.selling_date) or invoice_date
        due_date = _safe_date(invoice.due_date)

        return replace(
            invoice,
            invoice_date=invoice_date,
            selling_date=selling_date,
            due_date=due_date,
            payment_method=self._payment_method(invoice.payment_method),
            payment_status=self._payment_status(invoice.payment_status),
            status=invoice.status or InvoiceStatus.NEW,
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
                vat_rate=self._vat_rate(line.amount.vat_rate),
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
            "h": UnitOfMeasure.HOUR,
        }.get(str(value).lower(), UnitOfMeasure.PIECE)

    @staticmethod
    def _vat_rate(value) -> VatRate:
        return {
            "23": VatRate.VAT_23,
            "8": VatRate.VAT_8,
            "5": VatRate.VAT_5,
            "0": VatRate.VAT_0,
        }.get(str(value), VatRate.VAT_23)

    @staticmethod
    def _payment_method(value) -> PaymentMethod:
        return {
            "PAYU": PaymentMethod.BANK_TRANSFER,
            "TRANSFER": PaymentMethod.BANK_TRANSFER,
            "CASH": PaymentMethod.CASH,
            "CARD": PaymentMethod.CARD,
        }.get(str(value).upper(), PaymentMethod.UNKNOWN)

    @staticmethod
    def _payment_status(value) -> PaymentStatus:
        return {
            "PAID": PaymentStatus.PAID,
            "UNPAID": PaymentStatus.UNPAID,
            "PARTIALLY_PAID": PaymentStatus.PARTIALLY_PAID,
        }.get(str(value).upper(), PaymentStatus.UNPAID)
