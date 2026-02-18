from decimal import Decimal
from pathlib import Path

import pytest

from contract_costs.model.document import DocumentType
from contract_costs.model.financial_record import PaymentMethod, PaymentStatus
from contract_costs.services.documents.exeptions import DocumentFatalError
from contract_costs.ksef.parser.ksef_document_parser import KsefDocumentParser


NS = "http://crd.gov.pl/wzor/2025/06/25/13775/"


def _write_xml(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "ksef.xml"
    path.write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<k:Root xmlns:k="{NS}">{body}</k:Root>',
        encoding="utf-8",
    )
    return path


def test_parse_ksef_invoice_success(tmp_path):
    xml_path = _write_xml(
        tmp_path,
        """
        <k:Fa>
          <k:RodzajFaktury>VAT</k:RodzajFaktury>
          <k:P_2>FV/1/2026</k:P_2>
          <k:P_1>2026-02-10T00:00:00Z</k:P_1>
          <k:P_6>2026-02-10T00:00:00Z</k:P_6>
          <k:P_3>2026-02-20T00:00:00Z</k:P_3>
          <k:KodWaluty>PLN</k:KodWaluty>
          <k:P_13_1>100.00</k:P_13_1>
          <k:P_14_1>23.00</k:P_14_1>
          <k:P_15>123.00</k:P_15>
        </k:Fa>
        <k:Podmiot1>
          <k:DaneIdentyfikacyjne><k:Nazwa>Seller</k:Nazwa><k:NIP>2222222222</k:NIP></k:DaneIdentyfikacyjne>
          <k:Adres><k:AdresL1>Street 1</k:AdresL1><k:AdresL2>00-001 City</k:AdresL2><k:KodKraju>PL</k:KodKraju></k:Adres>
        </k:Podmiot1>
        <k:Podmiot2>
          <k:DaneIdentyfikacyjne><k:Nazwa>Buyer</k:Nazwa><k:NIP>1111111111</k:NIP></k:DaneIdentyfikacyjne>
          <k:Adres><k:AdresL1>Street 2</k:AdresL1><k:AdresL2>00-002 Town</k:AdresL2><k:KodKraju>PL</k:KodKraju></k:Adres>
        </k:Podmiot2>
        <k:Platnosc>
          <k:FormaPlatnosci>6</k:FormaPlatnosci>
          <k:DataZaplaty>2026-02-15T00:00:00Z</k:DataZaplaty>
          <k:Zaplacono>1</k:Zaplacono>
        </k:Platnosc>
        <k:FaWiersz>
          <k:P_7>Usluga</k:P_7>
          <k:P_8A>usluga</k:P_8A>
          <k:P_8B>1</k:P_8B>
          <k:P_11>100.00</k:P_11>
          <k:P_11Vat>23.00</k:P_11Vat>
          <k:P_12>23</k:P_12>
        </k:FaWiersz>
        """,
    )

    result = KsefDocumentParser().parse(xml_path)

    assert result.document_type == DocumentType.INVOICE
    assert result.record.reference == "FV/1/2026"
    assert result.record.payment_method == PaymentMethod.BANK_TRANSFER
    assert result.record.payment_status == PaymentStatus.PAID
    assert set(result.record.tags.split(",")) == {"ksef", "pln", "invoice"}
    assert len(result.lines) == 1
    assert result.lines[0].amount.net == Decimal("100.00")
    assert result.lines[0].amount.tax == Decimal("23.00")
    assert result.lines[0].amount.gross == Decimal("123.00")


def test_parse_ksef_correction_makes_amounts_negative(tmp_path):
    xml_path = _write_xml(
        tmp_path,
        """
        <k:Fa>
          <k:RodzajFaktury>KOR</k:RodzajFaktury>
          <k:P_2>FV/2/2026</k:P_2>
          <k:P_1>2026-02-10T00:00:00Z</k:P_1>
          <k:P_6>2026-02-10T00:00:00Z</k:P_6>
          <k:P_13_1>100.00</k:P_13_1>
          <k:P_14_1>23.00</k:P_14_1>
          <k:P_15>123.00</k:P_15>
        </k:Fa>
        <k:NrFaKorygowanej>FV/OLD/2025</k:NrFaKorygowanej>
        <k:Podmiot1><k:DaneIdentyfikacyjne><k:Nazwa>S</k:Nazwa><k:NIP>2</k:NIP></k:DaneIdentyfikacyjne></k:Podmiot1>
        <k:Podmiot2><k:DaneIdentyfikacyjne><k:Nazwa>B</k:Nazwa><k:NIP>1</k:NIP></k:DaneIdentyfikacyjne></k:Podmiot2>
        <k:FaWiersz>
          <k:P_7>Korekta</k:P_7>
          <k:P_8A>szt</k:P_8A>
          <k:P_8B>1</k:P_8B>
          <k:P_11A>123.00</k:P_11A>
          <k:P_11Vat>23.00</k:P_11Vat>
          <k:P_12>23</k:P_12>
        </k:FaWiersz>
        """,
    )

    result = KsefDocumentParser().parse(xml_path)

    assert result.document_type == DocumentType.CORRECTION
    assert result.record.reference == "FV/2/2026kor:FV/OLD/2025"
    assert result.lines[0].amount.net == Decimal("-100.00")
    assert result.lines[0].amount.tax == Decimal("-23.00")
    assert result.lines[0].amount.gross == Decimal("-123.00")


def test_parse_raises_document_fatal_error_for_invalid_xml(tmp_path):
    bad_path = tmp_path / "broken.xml"
    bad_path.write_text("<k:Root>", encoding="utf-8")

    with pytest.raises(DocumentFatalError, match="Invalid KSeF XML"):
        KsefDocumentParser().parse(bad_path)


def test_parse_raises_when_totals_do_not_match(tmp_path):
    xml_path = _write_xml(
        tmp_path,
        """
        <k:Fa>
          <k:RodzajFaktury>VAT</k:RodzajFaktury>
          <k:P_2>FV/X</k:P_2>
          <k:P_1>2026-02-10T00:00:00Z</k:P_1>
          <k:P_13_1>999.00</k:P_13_1>
          <k:P_14_1>23.00</k:P_14_1>
          <k:P_15>123.00</k:P_15>
        </k:Fa>
        <k:Podmiot1><k:DaneIdentyfikacyjne><k:Nazwa>S</k:Nazwa><k:NIP>2</k:NIP></k:DaneIdentyfikacyjne></k:Podmiot1>
        <k:Podmiot2><k:DaneIdentyfikacyjne><k:Nazwa>B</k:Nazwa><k:NIP>1</k:NIP></k:DaneIdentyfikacyjne></k:Podmiot2>
        <k:FaWiersz>
          <k:P_7>A</k:P_7><k:P_8A>szt</k:P_8A><k:P_8B>1</k:P_8B>
          <k:P_11>100.00</k:P_11><k:P_11Vat>23.00</k:P_11Vat><k:P_12>23</k:P_12>
        </k:FaWiersz>
        """,
    )

    with pytest.raises(DocumentFatalError, match="NET mismatch"):
        KsefDocumentParser().parse(xml_path)


def test_parse_maps_new_fa3_document_types(tmp_path):
    xml_path = _write_xml(
        tmp_path,
        """
        <k:Fa>
          <k:RodzajFaktury>ZAL</k:RodzajFaktury>
          <k:P_2>FV/ZAL/1</k:P_2>
          <k:P_1>2026-02-10T00:00:00Z</k:P_1>
          <k:P_13_1>100.00</k:P_13_1>
          <k:P_14_1>23.00</k:P_14_1>
          <k:P_15>123.00</k:P_15>
        </k:Fa>
        <k:Podmiot1><k:DaneIdentyfikacyjne><k:Nazwa>S</k:Nazwa><k:NIP>2</k:NIP></k:DaneIdentyfikacyjne></k:Podmiot1>
        <k:Podmiot2><k:DaneIdentyfikacyjne><k:Nazwa>B</k:Nazwa><k:NIP>1</k:NIP></k:DaneIdentyfikacyjne></k:Podmiot2>
        <k:FaWiersz>
          <k:P_7>A</k:P_7><k:P_8A>szt</k:P_8A><k:P_8B>1</k:P_8B>
          <k:P_11>100.00</k:P_11><k:P_11Vat>23.00</k:P_11Vat><k:P_12>23</k:P_12>
        </k:FaWiersz>
        """,
    )

    result = KsefDocumentParser().parse(xml_path)
    assert result.document_type == DocumentType.ADVANCE


def test_parse_maps_fa3_payment_codes(tmp_path):
    xml_path = _write_xml(
        tmp_path,
        """
        <k:Fa>
          <k:RodzajFaktury>VAT</k:RodzajFaktury>
          <k:P_2>FV/PAY/1</k:P_2>
          <k:P_1>2026-02-10T00:00:00Z</k:P_1>
          <k:P_13_1>100.00</k:P_13_1>
          <k:P_14_1>23.00</k:P_14_1>
          <k:P_15>123.00</k:P_15>
        </k:Fa>
        <k:Podmiot1><k:DaneIdentyfikacyjne><k:Nazwa>S</k:Nazwa><k:NIP>2</k:NIP></k:DaneIdentyfikacyjne></k:Podmiot1>
        <k:Podmiot2><k:DaneIdentyfikacyjne><k:Nazwa>B</k:Nazwa><k:NIP>1</k:NIP></k:DaneIdentyfikacyjne></k:Podmiot2>
        <k:Platnosc><k:FormaPlatnosci>1</k:FormaPlatnosci></k:Platnosc>
        <k:FaWiersz>
          <k:P_7>A</k:P_7><k:P_8A>szt</k:P_8A><k:P_8B>1</k:P_8B>
          <k:P_11>100.00</k:P_11><k:P_11Vat>23.00</k:P_11Vat><k:P_12>23</k:P_12>
        </k:FaWiersz>
        """,
    )

    result = KsefDocumentParser().parse(xml_path)
    assert result.record.payment_method == PaymentMethod.CASH
