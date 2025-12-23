from decimal import Decimal
from datetime import date

from contract_costs.services.invoices.dto.parse import (
    InvoiceParseResult,
    InvoiceUpdate,
    InvoiceLineUpdate,
    CompanyInput,
)

from contract_costs.model.amount import Amount, VatRate
from contract_costs.model.unit_of_measure import UnitOfMeasure
from contract_costs.model.invoice import PaymentMethod, PaymentStatus, InvoiceStatus


class AIInvoiceMapper:
    def map(self, data: dict) -> InvoiceParseResult:

        invoice = InvoiceUpdate(

            invoice_number=data.get("invoice_number"),
            invoice_date=self._date(data.get("invoice_date")),
            selling_date=self._date(data.get("selling_date")) or self._date(data.get("invoice_date")),
            buyer_id=None,
            seller_id=None,
            payment_method=self._payment_method(data.get("payment_method")),
            payment_status=self._payment_status(data.get("payment_status")),
            status=InvoiceStatus.NEW,
            due_date=self._date(data.get("due_date")),
        )

        lines = [
            InvoiceLineUpdate(
                invoice_line_id=None,
                invoice_id=None,
                item_name= item.get("item_name"),
                description= item.get("description"),
                quantity=Decimal(str(item.get("quantity") or "1")),
                unit=self._unit(item.get("unit")),
                amount=Amount(
                    value=Decimal(str(item.get("net_total") or "0")),
                    vat_rate=self._vat_rate(item.get("vat_rate")),
                ),
                contract_id=None,
                cost_node_id=None,
                cost_type_id=None,
            )
            for item in data.get("invoice_items", [])  # ✅ POPRAWKA
        ]

        buyer = CompanyInput(
            name=data.get("buyer_name"),
            tax_number=data.get("buyer_tax_number"),
            street=data.get("buyer_street"),
            city=data.get("buyer_city"),
            state=data.get("buyer_state"),
            zip_code=data.get("buyer_zip_code"),
            country=data.get("buyer_country"),
            bank_account=data.get("buyer_bank_account"),
            role="Client",
        )

        seller = CompanyInput(
            name=data.get("seller_name"),
            tax_number=data.get("seller_tax_number"),
            street=data.get("seller_street"),
            city=data.get("seller_city"),
            state=data.get("seller_state"),
            zip_code=data.get("seller_zip_code"),
            country=data.get("seller_country"),
            bank_account=data.get("seller_bank_account"),
            role="Client",
        )

        return InvoiceParseResult(
            invoice=invoice,
            lines=lines,
            buyer=buyer,
            seller=seller,
        )


    @staticmethod
    def _date(value: str | None) -> date | None:
        if not value:
            return None
        return date.fromisoformat(value)

    @staticmethod
    def _unit( value: str | None) -> UnitOfMeasure:
        if not value:
            return UnitOfMeasure.PIECE

        value = value.lower()
        return {
            "szt": UnitOfMeasure.PIECE,
            "pcs": UnitOfMeasure.PIECE,
            "kg": UnitOfMeasure.KILOGRAM,
            "m": UnitOfMeasure.METER,
            "m2": UnitOfMeasure.SQUARE_METER,
            "h": UnitOfMeasure.HOUR,
        }.get(value, UnitOfMeasure.PIECE)

    @staticmethod
    def _vat_rate( value: str | None) -> VatRate:
        return {
            "23": VatRate.VAT_23,
            "8": VatRate.VAT_8,
            "5": VatRate.VAT_5,
            "0": VatRate.VAT_0,
        }.get(str(value), VatRate.VAT_23)

    @staticmethod
    def _payment_method( value: str | None) -> PaymentMethod:
        return {
            "PAYU": PaymentMethod.BANK_TRANSFER,
            "TRANSFER": PaymentMethod.BANK_TRANSFER,
            "CASH": PaymentMethod.CASH,
            "CARD": PaymentMethod.CARD,
        }.get(value, PaymentMethod.BANK_TRANSFER)

    @staticmethod
    def _payment_status( value: str | None) -> PaymentStatus:
        return {
            "PAID": PaymentStatus.PAID,
            "UNPAID": PaymentStatus.UNPAID,
        }.get(value, PaymentStatus.UNPAID)
