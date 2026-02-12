import logging

from contract_costs.model.amount import Amount, VatRate, TaxTreatment, AmountInputType
from contract_costs.model.company import CompanyType
from contract_costs.model.document import DocumentType
from contract_costs.model.financial_record import PaymentMethod, PaymentStatus, FinancialRecordStatus
from contract_costs.model.unit_of_measure import UnitOfMeasure
from contract_costs.services.documents.exeptions import DocumentFatalError
from contract_costs.services.financial_records.assigment.apply.commands.invoice_command import InvoiceCommand
from contract_costs.services.financial_records.assigment.invoice_sources.dto.common import FinancialRecordUpdate, \
    FinancialRecordLineUpdate
from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.document_parser import \
    DocumentParser
from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.dto.parse import \
    DocumentParseResult, CompanyInput

from pathlib import Path
from datetime import datetime, date
from decimal import Decimal
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


class KsefDocumentParser(DocumentParser):

    NS = {"k": "http://crd.gov.pl/wzor/2025/06/25/13775/"}

    def parse(self, file_path: Path) -> DocumentParseResult:
        try:
            tree = ET.parse(file_path)
        except ET.ParseError as e:
            raise DocumentFatalError("Invalid KSeF XML") from e
        root = tree.getroot()

        # =========================
        # BASIC DATA
        # =========================
        invoice_number = self._text(root, ".//k:Fa/k:P_2")
        invoice_date = self._parse_date(self._text(root, ".//k:Fa/k:P_1"))
        selling_date = self._parse_date(self._text(root, ".//k:Fa/k:P_6"))

        due_date = self._parse_date(self._text(root, ".//k:Fa/k:P_3"))

        document_type = self._map_document_type(root)

        is_correction = document_type == DocumentType.CORRECTION
        old_reference = self._text(root, ".//k:NrFaKorygowanej")

        if is_correction:
            invoice_number = f"{invoice_number}kor:{old_reference}"
        # =========================
        # SELLER
        # =========================
        seller = CompanyInput(
            name=self._text(root, ".//k:Podmiot1/k:DaneIdentyfikacyjne/k:Nazwa"),
            tax_number=self._text(root, ".//k:Podmiot1/k:DaneIdentyfikacyjne/k:NIP"),
            street=self._text(root, ".//k:Podmiot1/k:Adres/k:AdresL1"),
            city=self._extract_city(root, ".//k:Podmiot1/k:Adres/k:AdresL2"),
            state=None,
            zip_code=self._extract_zip(root, ".//k:Podmiot1/k:Adres/k:AdresL2"),
            country=self._text(root, ".//k:Podmiot1/k:Adres/k:KodKraju"),
            phone_number=self._text(root, ".//k:Podmiot1/k:DaneKontaktowe/k:Telefon"),
            email=self._text(root, ".//k:Podmiot1/k:DaneKontaktowe/k:Email"),
            bank_account=self._text(root, ".//k:Platnosc/k:RachunekBankowy/k:NrRB"),
            role=CompanyType.SELLER.value
        )

        # =========================
        # BUYER
        # =========================
        buyer = CompanyInput(
            name=self._text(root, ".//k:Podmiot2/k:DaneIdentyfikacyjne/k:Nazwa"),
            tax_number=self._text(root, ".//k:Podmiot2/k:DaneIdentyfikacyjne/k:NIP"),
            street=self._text(root, ".//k:Podmiot2/k:Adres/k:AdresL1"),
            city=self._extract_city(root, ".//k:Podmiot2/k:Adres/k:AdresL2"),
            state=None,
            zip_code=self._extract_zip(root, ".//k:Podmiot2/k:Adres/k:AdresL2"),
            country=self._text(root, ".//k:Podmiot2/k:Adres/k:KodKraju"),
            phone_number=self._text(root, ".//k:Podmiot2/k:DaneKontaktowe/k:Telefon"),
            email=self._text(root, ".//k:Podmiot2/k:DaneKontaktowe/k:Email"),
            bank_account=None,
            role=CompanyType.BUYER.value
        )

        # =========================
        # PAYMENT
        # =========================
        payment_method_code = self._text(root, ".//k:Platnosc/k:FormaPlatnosci")
        paid_date = self._parse_date(self._text(root, ".//k:Platnosc/k:DataZaplaty"))

        payment_method = self._map_payment_method(payment_method_code)
        payment_status = self._map_payment_status(root)

        # =========================
        # LINES
        # =========================
        lines = []

        for row in root.findall(".//k:FaWiersz", self.NS):
            quantity = self._decimal(row, "k:P_8B")

            # raw_value = self._decimal(row, "k:P_11A")
            net_str = self._text(row, "k:P_11")
            gross_str = self._text(row, "k:P_11A")

            vat_value = self._decimal(row, "k:P_11Vat")

            vat_rate = self._map_vat_rate(self._text(row, "k:P_12"))

            if net_str:
                value = Decimal(net_str)
                input_type = AmountInputType.NET
            elif gross_str:
                value = Decimal(gross_str)
                input_type = AmountInputType.GROSS
            else:
                raise DocumentFatalError("Missing P_11 / P_11A")

            logger.info(
                "KSeF line interpreted as GROSS "
                "(value=%s, vat=%s, rate=%s)",
                value,
                vat_value,
                vat_rate.value
            )


            if is_correction:
                value = -abs(value)


            amount = Amount.from_input(
                value=value,
                input_type=input_type,
                vat_rate=vat_rate,
                tax_treatment=TaxTreatment.TAX_DEDUCTIBLE,
            )



            line = FinancialRecordLineUpdate(
                record_line_id=None,
                record_reference=invoice_number,
                item_name=self._text(row, "k:P_7"),
                description=None,
                quantity=quantity,
                unit=self._map_unit(self._text(row, "k:P_8A")),
                amount=amount,
                contract_id=None,
                contract_node_id=None,
                value_type_code=None
            )

            lines.append(line)

        # =========================
        # TOTAL VALIDATION
        # =========================
        self._validate_totals(root, lines, is_correction)

        # =========================
        # STATUS (COST / REVENUE)
        # =========================
        # my_tax_number = "TU_WSTAW_SWÓJ_NIP"  # albo wstrzyknij przez konstruktor
        #
        # financial_status = self._map_financial_status(
        #     seller_tax=seller.tax_number,
        #     buyer_tax=buyer.tax_number,
        #     my_tax=my_tax_number,
        # )
        financial_status = FinancialRecordStatus.DRAFT
        # =========================
        # TAGS
        # =========================
        currency = self._text(root, ".//k:Fa/k:KodWaluty") or "PLN"

        tags = {
            "ksef",
            currency.lower(),
            document_type.value,
        }

        # =========================
        # RECORD
        # =========================
        record = FinancialRecordUpdate(
            command=InvoiceCommand.APPLY,
            reference=invoice_number,
            record_id=None,
            old_reference=None,
            invoice_date=invoice_date,
            selling_date=selling_date,
            buyer_tax_number=buyer.tax_number,
            seller_tax_number=seller.tax_number,
            payment_method=payment_method,
            due_date=due_date,
            paid_date=paid_date,
            tags=",".join(tags),
            payment_status=payment_status,
            status=financial_status
        )

        return DocumentParseResult(
            document_type=document_type,
            record=record,
            lines=lines,
            buyer=buyer,
            seller=seller
        )

    # =====================================
    # Helpers
    # =====================================

    def _text(self, element, path):
        el = element.find(path, self.NS)
        return el.text.strip() if el is not None and el.text else None

    @staticmethod
    def _parse_date(value: str | None) -> date | None:
        if not value:
            return None
        return datetime.fromisoformat(value.replace("Z", "")).date()

    def _extract_zip(self, root, path):
        text = self._text(root, path)
        if not text:
            return None
        return text.split()[0] if "-" in text else None

    def _extract_city(self, root, path):
        text = self._text(root, path)
        if not text:
            return None
        parts = text.split()
        return " ".join(parts[1:]) if "-" in parts[0] else text

    @staticmethod
    def _map_vat_rate( value: str | None) -> VatRate:
        if value is None:
            return VatRate.VAT_ZW  # fallback (możesz zmienić)

        value = value.strip().lower()

        mapping = {
            "23": VatRate.VAT_23,
            "8": VatRate.VAT_8,
            "5": VatRate.VAT_5,
            "0": VatRate.VAT_0,
            "zw": VatRate.VAT_ZW,
        }

        return mapping.get(value, VatRate.VAT_23)

    @staticmethod
    def _map_payment_method( value: str | None) -> PaymentMethod:
        if value is None:
            return PaymentMethod.UNKNOWN

        mapping = {
            "1": PaymentMethod.BANK_TRANSFER,
            "2": PaymentMethod.CASH,
            "3": PaymentMethod.CARD,
            "4": PaymentMethod.PRE_PAID,
        }

        return mapping.get(value, PaymentMethod.UNKNOWN)

    @staticmethod
    def _map_unit(value: str | None) -> UnitOfMeasure:
        if not value:
            return UnitOfMeasure.UNKNOWN

        normalized = value.strip().lower().replace(".", "")

        mapping = {
            "szt": UnitOfMeasure.PIECE,
            "m": UnitOfMeasure.METER,
            "m2": UnitOfMeasure.SQUARE_METER,
            "m3": UnitOfMeasure.CUBIC_METER,
            "kg": UnitOfMeasure.KILOGRAM,
            "t": UnitOfMeasure.TON,
            "h": UnitOfMeasure.HOUR,
            "godz": UnitOfMeasure.HOUR,
            "l": UnitOfMeasure.LITER,
            "usl": UnitOfMeasure.SERVICE,
            "usluga": UnitOfMeasure.SERVICE,
            "usługi": UnitOfMeasure.SERVICE,
            "day": UnitOfMeasure.DAY,
        }

        return mapping.get(normalized, UnitOfMeasure.UNKNOWN)

    def _map_document_type(self, root) -> DocumentType:
        rodzaj = self._text(root, ".//k:RodzajFaktury")

        if rodzaj == "VAT":
            return DocumentType.INVOICE

        if rodzaj == "KOREKTA":
            return DocumentType.CORRECTION

        return DocumentType.UNKNOWN

    @staticmethod
    def _map_financial_status( seller_tax: str, buyer_tax: str, my_tax: str):
        if seller_tax == my_tax:
            return FinancialRecordStatus.NEW_REVENUE
        return FinancialRecordStatus.NEW_COST

    def _map_payment_status(self, root) -> PaymentStatus:
        paid = self._text(root, ".//k:Platnosc/k:Zaplacono")

        if paid == "1":
            return PaymentStatus.PAID

        return PaymentStatus.UNPAID

    def _validate_totals(self, root, lines: list[FinancialRecordLineUpdate], is_correction: bool):
        ksef_net = Decimal(self._text(root, ".//k:Fa/k:P_13_1"))
        ksef_vat = Decimal(self._text(root, ".//k:Fa/k:P_14_1"))
        ksef_gross = Decimal(self._text(root, ".//k:Fa/k:P_15"))

        if is_correction:
            ksef_net = -abs(ksef_net)
            ksef_vat = -abs(ksef_vat)
            ksef_gross = -abs(ksef_gross)

        domain_net = sum((l.amount.net for l in lines),Decimal("0")).quantize(Decimal("0.01"))
        domain_vat = sum((l.amount.tax for l in lines),Decimal("0")).quantize(Decimal("0.01"))
        domain_gross = sum((l.amount.gross for l in lines),Decimal("0")).quantize(Decimal("0.01"))


        if not self._almost_equal(ksef_net, domain_net):
            raise DocumentFatalError(f"NET mismatch KSeF={ksef_net} domain={domain_net}")

        if not self._almost_equal(ksef_vat, domain_vat):
            raise DocumentFatalError(f"VAT mismatch KSeF={ksef_vat} domain={domain_vat}")

        if not self._almost_equal(ksef_gross, domain_gross):
            raise DocumentFatalError(f"GROSS mismatch KSeF={ksef_gross} domain={domain_gross}")

    @staticmethod
    def _almost_equal(a: Decimal, b: Decimal, tolerance: Decimal = Decimal("0.02")) -> bool:
        return abs(a - b) <= tolerance

    def _decimal(self, element, path) -> Decimal:
        value = self._text(element, path)
        if not value:
            return Decimal("0")
        return Decimal(value)