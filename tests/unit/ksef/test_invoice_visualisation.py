import socket
from pathlib import Path

import pytest

from contract_costs.ksef.render.invoice_visualisation import (
    UnsupportedInvoiceSchema,
    render_invoice_html,
)

FA3_NS = "http://crd.gov.pl/wzor/2025/06/25/13775/"

FA3_INVOICE = f"""<?xml version="1.0" encoding="UTF-8"?>
<Faktura xmlns="{FA3_NS}">
  <Naglowek>
    <KodFormularza kodSystemowy="FA (3)" wersjaSchemy="1-0E">FA</KodFormularza>
    <WariantFormularza>3</WariantFormularza>
    <DataWytworzeniaFa>2026-09-15T10:00:00Z</DataWytworzeniaFa>
    <SystemInfo>Test</SystemInfo>
  </Naglowek>
  <Podmiot1>
    <DaneIdentyfikacyjne><NIP>2222222222</NIP><Nazwa>Hurtownia Testowa Sp. z o.o.</Nazwa></DaneIdentyfikacyjne>
    <Adres><KodKraju>PL</KodKraju><AdresL1>ul. Testowa 1</AdresL1><AdresL2>00-001 Warszawa</AdresL2></Adres>
  </Podmiot1>
  <Podmiot2>
    <DaneIdentyfikacyjne><NIP>1111111111</NIP><Nazwa>Nabywca Próbny</Nazwa></DaneIdentyfikacyjne>
    <Adres><KodKraju>PL</KodKraju><AdresL1>ul. Kupiecka 2</AdresL1><AdresL2>31-010 Kraków</AdresL2></Adres>
    <JST>2</JST><GV>2</GV>
  </Podmiot2>
  <Fa>
    <KodWaluty>PLN</KodWaluty>
    <P_1>2026-09-15</P_1>
    <P_2>FV/7/2026</P_2>
    <P_13_1>100.00</P_13_1>
    <P_14_1>23.00</P_14_1>
    <P_15>123.00</P_15>
    <Adnotacje>
      <P_16>2</P_16><P_17>2</P_17><P_18>2</P_18><P_18A>2</P_18A>
      <Zwolnienie><P_19N>1</P_19N></Zwolnienie>
      <NoweSrodkiTransportu><P_22N>1</P_22N></NoweSrodkiTransportu>
      <P_23>2</P_23>
      <PMarzy><P_PMarzyN>1</P_PMarzyN></PMarzy>
    </Adnotacje>
    <RodzajFaktury>VAT</RodzajFaktury>
    <FaWiersz>
      <NrWierszaFa>1</NrWierszaFa>
      <P_7>Usługa montażu</P_7>
      <P_8A>szt</P_8A>
      <P_8B>1</P_8B>
      <P_9A>100.00</P_9A>
      <P_11>100.00</P_11>
      <P_12>23</P_12>
    </FaWiersz>
    <Platnosc>
      <Zaplacono>1</Zaplacono>
      <DataZaplaty>2026-09-15</DataZaplaty>
      <FormaPlatnosci>1</FormaPlatnosci>
    </Platnosc>
  </Fa>
</Faktura>
"""


@pytest.fixture
def no_network(monkeypatch):
    def blocked(*args, **kwargs):
        raise AssertionError("visualisation must not use the network")

    monkeypatch.setattr(socket.socket, "connect", blocked)


def _write(tmp_path: Path, content: str) -> Path:
    path = tmp_path / "invoice.xml"
    path.write_text(content, encoding="utf-8")
    return path


def test_renders_fa3_invoice_with_official_stylesheet_offline(tmp_path, no_network):
    html = render_invoice_html(_write(tmp_path, FA3_INVOICE))

    assert "FV/7/2026" in html
    assert "Hurtownia Testowa Sp. z o.o." in html
    assert "Nabywca Próbny" in html
    assert "Usługa montażu" in html
    # nazwa kraju pochodzi ze słownika MF (KodyKrajow), który musi być czytany lokalnie
    assert "POLSKA" in html


def test_unknown_namespace_is_rejected(tmp_path, no_network):
    path = _write(tmp_path, '<?xml version="1.0"?><Faktura xmlns="urn:other"/>')

    with pytest.raises(UnsupportedInvoiceSchema):
        render_invoice_html(path)


def test_empty_line_item_columns_are_dropped(tmp_path, no_network):
    html = render_invoice_html(_write(tmp_path, FA3_INVOICE))

    assert "Nazwa (rodzaj) towaru lub usługi" in html
    # kolumna „Indeks” jest pusta we wszystkich pozycjach
    assert ">Indeks<" not in html
