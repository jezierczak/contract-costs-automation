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


class UnsupportedInvoiceSchema(Exception):
    pass


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
    return str(_transform(stylesheet_url)(document))
