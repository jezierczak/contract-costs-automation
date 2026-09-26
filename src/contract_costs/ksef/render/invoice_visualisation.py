"""
Wizualizacja faktur KSeF oficjalnym arkuszem XSL Ministerstwa Finansów.

Arkusze i słowniki MF leżą w resources/crd.gov.pl/ bez zmian, w ścieżkach
odwzorowujących adresy http://crd.gov.pl/... – resolver podsuwa lokalne kopie
zamiast pobierać je z sieci. Aktualizacja = podmiana plików.
"""
from functools import lru_cache
from pathlib import Path

from lxml import etree

CRD_URL_PREFIXES = ("http://crd.gov.pl/", "https://crd.gov.pl/")
CRD_ROOT = Path(__file__).resolve().parents[2] / "resources" / "crd.gov.pl"

# namespace faktury -> arkusz wizualizacji MF
STYLESHEETS: dict[str, str] = {
    "http://crd.gov.pl/wzor/2025/06/25/13775/": "http://crd.gov.pl/wzor/2025/06/25/13775/styl.xsl",  # FA(3)
}


# style MF są pisane pod ekran (5% marginesu, szare tła, 11pt) – do wydruku A4
PRINT_CSS = """
@page { size: A4; margin: 12mm 10mm 14mm 10mm;
        @bottom-right { content: counter(page) " / " counter(pages); font-size: 7pt; color: #666; } }
body { padding: 0 !important; margin: 0 !important; font-size: 8.5pt; }
div.body { min-width: 0 !important; }
div.deklaracja, div.zalacznik { margin: 0 !important; }
table { width: 100% !important; max-width: 100%; }
td, th { padding: 1px 3px !important; vertical-align: top; }
.lewa, .srodek, .prawa, .wypelniane, .puste2 { font-size: 1em !important; }
.niewypelniane, .puste, .niewypelnianeopisy, .center { font-size: 0.85em !important; }
/* tabele pozycji i podsumowań – dużo kolumn, muszą się zmieścić w szerokości A4 */
table.white-space td { font-size: 6.8pt !important; overflow-wrap: anywhere; hyphens: auto; }
table.white-space td.niewypelniane { font-size: 6pt !important; }
table.white-space td.prawa, table.white-space td.srodek { white-space: nowrap !important; overflow-wrap: normal; }
tr { page-break-inside: avoid; }
br + br { display: none; }
.naglowek, .tytul-sekcja-blok, .niewypelniane, .ukryte, .tlo-zalacznika, .tlo-formularza {
    -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.kod-formularza, .tytul { font-size: 1.5em !important; }
"""


class UnsupportedInvoiceSchema(Exception):
    pass


class PdfRenderingUnavailable(Exception):
    """WeasyPrint nie działa w tym środowisku (np. Windows bez GTK/Pango)."""


def _local_path(url: str) -> Path | None:
    for prefix in CRD_URL_PREFIXES:
        if url.startswith(prefix):
            path = CRD_ROOT / url[len(prefix):]
            return path if path.is_file() else None
    return None


class _CrdResolver(etree.Resolver):
    def resolve(self, system_url, public_id, context):  # type: ignore[override]
        path = _local_path(system_url or "")
        if path is None:
            return None
        return self.resolve_filename(str(path), context)  # type: ignore[attr-defined]


def _parser() -> etree.XMLParser:
    parser = etree.XMLParser(no_network=True, resolve_entities=False)
    parser.resolvers.add(_CrdResolver())
    return parser


@lru_cache(maxsize=None)
def _transform(stylesheet_url: str) -> etree.XSLT:
    path = _local_path(stylesheet_url)
    if path is None:
        raise UnsupportedInvoiceSchema(f"Missing local stylesheet for {stylesheet_url}")
    stylesheet = etree.parse(str(path), _parser(), base_url=stylesheet_url)
    return etree.XSLT(stylesheet)


def render_invoice_html(xml_path: Path) -> str:
    document = etree.parse(str(xml_path), etree.XMLParser(no_network=True, resolve_entities=False))
    namespace = etree.QName(document.getroot()).namespace
    stylesheet_url = STYLESHEETS.get(namespace or "")
    if stylesheet_url is None:
        raise UnsupportedInvoiceSchema(f"No visualisation for namespace {namespace}")
    result = _transform(stylesheet_url)(document)
    _drop_empty_columns(result.getroot())
    return str(result)


def _drop_empty_columns(root) -> None:
    """
    Arkusz MF pokazuje w tabeli pozycji wszystkie ~20 kolumn FA(3), zwykle w
    większości puste – usuwamy kolumny bez wartości w żadnym wierszu danych.
    """
    if root is None:
        return
    for table in root.iter("table"):
        if "white-space" not in (table.get("class") or "").split():
            continue
        rows = [row for row in table.iter("tr") if len(row)]
        if len(rows) < 2 or any(cell.get("colspan") for row in rows for cell in row):
            continue
        width = len(rows[0])
        if any(len(row) != width for row in rows):
            continue
        empty = [
            index for index in range(width)
            if all(not "".join(row[index].itertext()).strip() for row in rows[1:])
        ]
        for row in rows:
            for index in reversed(empty):
                row.remove(row[index])


def render_invoice_pdf(xml_path: Path) -> bytes:
    html = render_invoice_html(xml_path)
    try:
        from weasyprint import CSS, HTML
    except OSError as e:  # brak bibliotek systemowych Pango
        raise PdfRenderingUnavailable(str(e)) from e
    return HTML(string=html).write_pdf(stylesheets=[CSS(string=PRINT_CSS)])

