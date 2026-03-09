import logging
import os
import xml.etree.ElementTree as ET
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path


from contract_costs.model.amount import Amount, AmountInputType, TaxTreatment, VatRate
from contract_costs.model.company import CompanyType
from contract_costs.model.document import DocumentType
from contract_costs.model.financial_record import (
    FinancialRecordStatus,
    PaymentMethod,
    PaymentStatus,
)
from contract_costs.model.unit_of_measure import UnitOfMeasure
from contract_costs.services.documents.exeptions import DocumentFatalError
from contract_costs.services.financial_records.assigment.apply.commands.invoice_command import (
    InvoiceCommand,
)
from contract_costs.services.financial_records.assigment.invoice_sources.dto.common import (
    FinancialRecordLineUpdate,
    FinancialRecordUpdate,
)
from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.document_parser import (
    DocumentParser,
)
from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.dto.parse import (
    CompanyInput,
    DocumentParseResult,
)

logger = logging.getLogger(__name__)


class KsefDocumentParser(DocumentParser):
    NS = {"k": "http://crd.gov.pl/wzor/2025/06/25/13775/"}

    def parse(self, file_path: Path) -> DocumentParseResult:
        try:
            root = ET.parse(file_path).getroot()
        except ET.ParseError as e:
            raise DocumentFatalError("Invalid KSeF XML") from e

        self._validate_xsd_if_configured(file_path)
        self._validate_structure(root)

        invoice_number = self._text(root, ".//k:Fa/k:P_2")
        invoice_date = self._parse_date(self._text(root, ".//k:Fa/k:P_1"))
        selling_date = self._parse_date(self._text(root, ".//k:Fa/k:P_6"))
        due_date = (
            self._parse_date(self._text(root, ".//k:Platnosc/k:TerminPlatnosci/k:Termin"))
            or self._parse_date(self._text(root, ".//k:Fa/k:P_3"))
        )

        document_type = self._map_document_type(root)
        is_correction = document_type in {
            DocumentType.CORRECTION,
            DocumentType.CORRECTION_ADVANCE,
            DocumentType.CORRECTION_SETTLEMENT,
        }

        old_reference = self._text(root, ".//k:NrFaKorygowanej")
        if is_correction and old_reference:
            invoice_number = f"{invoice_number}kor:{old_reference}"

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
            role=CompanyType.SELLER.value,
        )

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
            role=CompanyType.BUYER.value,
        )

        payment_method_code = self._text(root, ".//k:Platnosc/k:FormaPlatnosci")
        paid_date = self._parse_date(self._text(root, ".//k:Platnosc/k:DataZaplaty"))
        payment_method = self._map_payment_method(payment_method_code)
        payment_status = self._map_payment_status(root)

        lines = self._parse_fa_wiersz(root, invoice_number, is_correction)
        if not lines:
            logger.info("No FaWiersz found; fallback to ZamowienieWiersz")
            lines = self._parse_zamowienie_wiersz(root, invoice_number, is_correction)
        if not lines:
            raise DocumentFatalError("No invoice lines found (FaWiersz/ZamowienieWiersz)")

        self._validate_totals(root, lines, is_correction)

        currency = self._text(root, ".//k:Fa/k:KodWaluty") or "PLN"
        tags = {"ksef", currency.lower(), document_type.value}

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
            status=FinancialRecordStatus.DRAFT,
        )


        return DocumentParseResult(
            document_type=document_type,
            record=record,
            lines=lines,
            buyer=buyer,
            seller=seller,
        )

    def _parse_fa_wiersz(self, root, invoice_number: str, is_correction: bool):
        lines = []
        for row in root.findall(".//k:FaWiersz", self.NS):
            lines.append(
                self._build_line_from_row(
                    row=row,
                    invoice_number=invoice_number,
                    is_correction=is_correction,
                    name_path="k:P_7",
                    unit_path="k:P_8A",
                    qty_path="k:P_8B",
                    net_path="k:P_11",
                    gross_path="k:P_11A",
                    vat_path="k:P_11Vat",
                    vat_rate_path="k:P_12",
                )
            )
        return lines

    def _parse_zamowienie_wiersz(self, root, invoice_number: str, is_correction: bool):
        lines = []
        for row in root.findall(".//k:ZamowienieWiersz", self.NS):
            lines.append(
                self._build_line_from_row(
                    row=row,
                    invoice_number=invoice_number,
                    is_correction=is_correction,
                    name_path="k:P_7Z",
                    unit_path="k:P_8AZ",
                    qty_path="k:P_8BZ",
                    net_path="k:P_11NettoZ",
                    gross_path=None,
                    vat_path="k:P_11VatZ",
                    vat_rate_path="k:P_12Z",
                )
            )
        return lines

    def _build_line_from_row(
        self,
        *,
        row,
        invoice_number: str,
        is_correction: bool,
        name_path: str,
        unit_path: str,
        qty_path: str,
        net_path: str | None,
        gross_path: str | None,
        vat_path: str,
        vat_rate_path: str,
    ) -> FinancialRecordLineUpdate:
        quantity = self._decimal(row, qty_path)

        net_str = self._text(row, net_path) if net_path else None
        gross_str = self._text(row, gross_path) if gross_path else None
        vat_value = self._decimal_from_text(self._text(row, vat_path))

        if net_str:
            value = self._decimal_from_text(net_str)
            input_type = AmountInputType.NET
        elif gross_str:
            value = self._decimal_from_text(gross_str)
            input_type = AmountInputType.GROSS
        else:
            raise DocumentFatalError("Missing net/gross value in line")

        vat_rate = self._resolve_vat_rate(
            declared_rate=self._text(row, vat_rate_path),
            input_type=input_type,
            value=value,
            vat_value=vat_value,
        )

        if is_correction:
            value = -abs(value)

        amount = Amount.from_input(
            value=value,
            input_type=input_type,
            vat_rate=vat_rate,
            tax_treatment=TaxTreatment.TAX_DEDUCTIBLE,
        )

        return FinancialRecordLineUpdate(
            record_line_id=None,
            record_reference=invoice_number,
            item_name=self._text(row, name_path),
            description=None,
            quantity=quantity,
            unit=self._map_unit(self._text(row, unit_path)),
            amount=amount,
            contract_reference=None,
            contract_node_reference=None,
            value_type_reference=None,
            agreement_reference=None,
            agreement_node_reference=None
        )

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
        return " ".join(parts[1:]) if parts and "-" in parts[0] else text

    @staticmethod
    def _map_vat_rate(value: str | None) -> VatRate:
        if value is None:
            return VatRate.VAT_ZW

        normalized = value.strip().lower().replace("%", "")
        mapping = {
            "23": VatRate.VAT_23,
            "22": VatRate.VAT_23,
            "8": VatRate.VAT_8,
            "7": VatRate.VAT_8,
            "5": VatRate.VAT_5,
            "0": VatRate.VAT_0,
            "zw": VatRate.VAT_ZW,
            "oo": VatRate.VAT_ZW,
            "np": VatRate.VAT_ZW,
        }
        return mapping.get(normalized, VatRate.VAT_ZW)

    def _resolve_vat_rate(
        self,
        *,
        declared_rate: str | None,
        input_type: AmountInputType,
        value: Decimal,
        vat_value: Decimal,
    ) -> VatRate:
        direct = self._map_vat_rate(declared_rate)
        if direct != VatRate.VAT_ZW:
            return direct

        if vat_value == Decimal("0"):
            return VatRate.VAT_ZW

        if input_type == AmountInputType.NET and value != 0:
            ratio = (vat_value / value).copy_abs()
            return self._closest_vat_rate(ratio)

        if input_type == AmountInputType.GROSS and value != 0:
            net = value - vat_value
            if net != 0:
                ratio = (vat_value / net).copy_abs()
                return self._closest_vat_rate(ratio)

        return VatRate.VAT_ZW

    @staticmethod
    def _closest_vat_rate(ratio: Decimal) -> VatRate:
        allowed: dict[Decimal, VatRate] = {
            Decimal("0.23"): VatRate.VAT_23,
            Decimal("0.08"): VatRate.VAT_8,
            Decimal("0.05"): VatRate.VAT_5,
            Decimal("0.00"): VatRate.VAT_0,
        }

        best_rate = min(allowed.keys(), key=lambda rate: abs(rate - ratio))

        if abs(best_rate - ratio) <= Decimal("0.02"):
            return allowed[best_rate]
        return VatRate.VAT_ZW

    @staticmethod
    def _map_payment_method(value: str | None) -> PaymentMethod:
        if value is None:
            return PaymentMethod.UNKNOWN

        mapping = {
            "1": PaymentMethod.CASH,
            "2": PaymentMethod.CARD,
            "3": PaymentMethod.BON,
            "4": PaymentMethod.CHECK,
            "5": PaymentMethod.CREDIT,
            "6": PaymentMethod.BANK_TRANSFER,
            "7": PaymentMethod.BLIK,
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
            "uslugi": UnitOfMeasure.SERVICE,
            "day": UnitOfMeasure.DAY,
        }
        return mapping.get(normalized, UnitOfMeasure.UNKNOWN)

    def _map_document_type(self, root) -> DocumentType:
        rodzaj = (self._text(root, ".//k:RodzajFaktury") or "").strip().upper()
        mapping = {
            "VAT": DocumentType.INVOICE,
            "KOR": DocumentType.CORRECTION,
            "KOREKTA": DocumentType.CORRECTION,
            "ZAL": DocumentType.ADVANCE,
            "ROZ": DocumentType.SETTLEMENT,
            "UPR": DocumentType.SIMPLIFIED,
            "KOR_ZAL": DocumentType.CORRECTION_ADVANCE,
            "KOR_ROZ": DocumentType.CORRECTION_SETTLEMENT,
        }
        return mapping.get(rodzaj, DocumentType.UNKNOWN)

    def _map_payment_status(self, root) -> PaymentStatus:
        paid = self._text(root, ".//k:Platnosc/k:Zaplacono")
        if paid == "1":
            return PaymentStatus.PAID
        return PaymentStatus.UNPAID

    def _validate_totals(
        self,
        root,
        lines: list[FinancialRecordLineUpdate],
        is_correction: bool,
    ) -> None:
        net_paths = [
            ".//k:Fa/k:P_13_1",
            ".//k:Fa/k:P_13_2",
            ".//k:Fa/k:P_13_3",
            ".//k:Fa/k:P_13_4",
            ".//k:Fa/k:P_13_5",
            ".//k:Fa/k:P_13_6_1",
            ".//k:Fa/k:P_13_6_2",
            ".//k:Fa/k:P_13_6_3",
            ".//k:Fa/k:P_13_7",
            ".//k:Fa/k:P_13_8",
            ".//k:Fa/k:P_13_9",
            ".//k:Fa/k:P_13_10",
            ".//k:Fa/k:P_13_11",
        ]
        vat_paths = [
            ".//k:Fa/k:P_14_1",
            ".//k:Fa/k:P_14_2",
            ".//k:Fa/k:P_14_3",
            ".//k:Fa/k:P_14_4",
            ".//k:Fa/k:P_14_5",
        ]

        ksef_net = sum((self._decimal_or_zero(root, p) for p in net_paths), Decimal("0"))
        ksef_vat = sum((self._decimal_or_zero(root, p) for p in vat_paths), Decimal("0"))
        p15 = self._decimal_or_zero(root, ".//k:Fa/k:P_15")
        ksef_gross = p15 if p15 != 0 else (ksef_net + ksef_vat)

        if is_correction:
            ksef_net = -abs(ksef_net)
            ksef_vat = -abs(ksef_vat)
            ksef_gross = -abs(ksef_gross)

        domain_net = sum((l.amount.net for l in lines), Decimal("0")).quantize(Decimal("0.01"))
        domain_vat = sum((l.amount.tax for l in lines), Decimal("0")).quantize(Decimal("0.01"))
        domain_gross = sum((l.amount.gross for l in lines), Decimal("0")).quantize(Decimal("0.01"))

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
        return self._decimal_from_text(value)

    def _decimal_or_zero(self, element, path) -> Decimal:
        value = self._text(element, path)
        return self._decimal_from_text(value)

    @staticmethod
    def _decimal_from_text(value: str | None) -> Decimal:
        if not value:
            return Decimal("0")
        try:
            return Decimal(value)
        except InvalidOperation as e:
            raise DocumentFatalError(f"Invalid decimal value: {value}") from e

    def _validate_structure(self, root) -> None:
        # Lightweight compliance check (not full XSD validation).
        if root.tag.startswith("{") and self.NS["k"] not in root.tag:
            raise DocumentFatalError("Unsupported XML namespace for KSeF FA(3)")

        required = {
            "Fa/P_2": self._text(root, ".//k:Fa/k:P_2"),
            "Fa/P_1": self._text(root, ".//k:Fa/k:P_1"),
            "Podmiot1/NIP": self._text(root, ".//k:Podmiot1/k:DaneIdentyfikacyjne/k:NIP"),
            "Podmiot2/NIP": self._text(root, ".//k:Podmiot2/k:DaneIdentyfikacyjne/k:NIP"),
        }
        missing = [name for name, val in required.items() if not val]
        if missing:
            raise DocumentFatalError(f"Missing required KSeF fields: {', '.join(missing)}")

        rodzaj = (self._text(root, ".//k:RodzajFaktury") or "").strip().upper()
        allowed = {"VAT", "KOR", "KOREKTA", "ZAL", "ROZ", "UPR", "KOR_ZAL", "KOR_ROZ"}
        if rodzaj and rodzaj not in allowed:
            raise DocumentFatalError(f"Unsupported RodzajFaktury: {rodzaj}")

    def _validate_xsd_if_configured(self, file_path: Path) -> None:
        xsd_path = os.getenv("KSEF_FA3_XSD_PATH")
        if not xsd_path:
            return

        try:
            from lxml import etree  # type: ignore
        except Exception:
            logger.warning("KSEF_FA3_XSD_PATH set but lxml not installed; skipping XSD validation")
            return

        schema_file = Path(xsd_path)
        if not schema_file.exists():
            raise DocumentFatalError(f"Configured XSD not found: {schema_file}")

        try:
            schema_doc = etree.parse(str(schema_file))
            schema = etree.XMLSchema(schema_doc)
            xml_doc = etree.parse(str(file_path))
            schema.assertValid(xml_doc)
        except Exception as e:
            raise DocumentFatalError(f"XSD validation failed: {e}") from e
