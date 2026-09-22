from __future__ import annotations

import logging
import os
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from ksef_client import KsefClient, KsefClientOptions
from ksef_client import KsefEnvironment as LibKsefEnvironment
from ksef_client.client import InvoicesClient
from ksef_client.models import InvoiceQueryDateType, InvoiceQuerySubjectType
from ksef_client.openapi_models import InvoiceMetadata
from ksef_client.services import AuthCoordinator
from ksef_client.services.xades import XadesKeyPair

from contract_costs.infrastructure.secrets_cipher import decrypt_secret

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class KsefDownloadedInvoice:
    external_id: str
    filename: str
    xml_content: bytes


class KsefApiClient:
    """
    KSeF API 2.0 client wrapper (delegates the protocol/crypto to the
    `ksef-client` PyPI SDK: https://github.com/smekcio/ksef-client-python).

    Modes:
    - mock (default): reads XML files from KSEF_MOCK_XML_DIR
    - http: real KSeF API, authenticated with the company's qualified
      certificate (XAdES) stored in CompanyKsefSettings
    """

    _PAGE_SIZE = 100
    _MAX_PAGES = 200  # safety guard against runaway pagination
    _SUBJECT_IDENTIFIER_TYPE = "certificateSubject"

    def __init__(self, *, mode: str | None = None) -> None:
        self._mode = (mode or os.getenv("KSEF_IMPORT_MODE") or "mock").strip().lower()

    def fetch_invoice_xmls(
        self,
        *,
        settings,
        company,
        from_date: date,
        to_date: date,
    ) -> list[KsefDownloadedInvoice]:
        if self._mode == "mock":
            return self._fetch_mock(company=company)
        if self._mode == "http":
            return self._fetch_ksef(
                settings=settings,
                company=company,
                from_date=from_date,
                to_date=to_date,
            )
        raise RuntimeError(f"Unsupported KSeF import mode: {self._mode}")

    def _fetch_mock(self, *, company) -> list[KsefDownloadedInvoice]:
        mock_dir_raw = os.getenv("KSEF_MOCK_XML_DIR")
        if not mock_dir_raw:
            return []

        mock_dir = Path(mock_dir_raw)
        if not mock_dir.exists() or not mock_dir.is_dir():
            raise RuntimeError(f"KSEF_MOCK_XML_DIR does not exist: {mock_dir}")

        limit = int(os.getenv("KSEF_MOCK_LIMIT", "20"))
        files = sorted(mock_dir.glob("*.xml"))[:limit]

        result: list[KsefDownloadedInvoice] = []
        for xml_file in files:
            result.append(
                KsefDownloadedInvoice(
                    external_id=f"mock-{xml_file.stem}",
                    filename=f"ksef_{company.tax_number}_{xml_file.name}",
                    xml_content=xml_file.read_bytes(),
                )
            )
        return result

    def _fetch_ksef(
        self,
        *,
        settings,
        company,
        from_date: date,
        to_date: date,
    ) -> list[KsefDownloadedInvoice]:
        if not settings.certificate_path:
            raise RuntimeError(
                f"Missing certificate_path in KSeF settings for company {company.tax_number}"
            )

        base_url = LibKsefEnvironment[settings.environment.name].value

        certificate_password = (
            decrypt_secret(settings.certificate_password)
            if settings.certificate_password
            else None
        )

        with KsefClient(KsefClientOptions(base_url=base_url)) as client:
            key_pair = XadesKeyPair.from_pkcs12_file(
                pkcs12_path=settings.certificate_path,
                pkcs12_password=certificate_password,
            )
            auth_result = AuthCoordinator(client.auth).authenticate_with_xades_key_pair(
                key_pair=key_pair,
                context_identifier_type="nip",
                context_identifier_value=company.tax_number,
                subject_identifier_type=self._SUBJECT_IDENTIFIER_TYPE,
            )
            access_token = auth_result.access_token

            date_from = f"{from_date.isoformat()}T00:00:00Z"
            date_to = f"{to_date.isoformat()}T23:59:59Z"

            seen_ksef_numbers: set[str] = set()
            result: list[KsefDownloadedInvoice] = []

            # Faktury, w których firma jest sprzedawcą (Subject1 – przychody)
            # i nabywcą (Subject2 – koszty) – pobieramy obie role.
            for subject_type in (
                InvoiceQuerySubjectType.SUBJECT1,
                InvoiceQuerySubjectType.SUBJECT2,
            ):
                for metadata in self._iter_invoice_metadata(
                    invoices_client=client.invoices,
                    subject_type=subject_type,
                    date_from=date_from,
                    date_to=date_to,
                    access_token=access_token,
                ):
                    if metadata.ksef_number in seen_ksef_numbers:
                        continue
                    seen_ksef_numbers.add(metadata.ksef_number)

                    content = client.invoices.get_invoice_bytes(
                        ksef_number=metadata.ksef_number,
                        access_token=access_token,
                    )
                    result.append(
                        KsefDownloadedInvoice(
                            external_id=metadata.ksef_number,
                            filename=f"ksef_{company.tax_number}_{metadata.ksef_number}.xml",
                            xml_content=content.content,
                        )
                    )

            return result

    def _iter_invoice_metadata(
        self,
        *,
        invoices_client: InvoicesClient,
        subject_type: InvoiceQuerySubjectType,
        date_from: str,
        date_to: str,
        access_token: str,
    ) -> Iterator[InvoiceMetadata]:
        offset = 0
        for _ in range(self._MAX_PAGES):
            response = invoices_client.query_invoice_metadata_by_date_range(
                subject_type=subject_type,
                date_type=InvoiceQueryDateType.ISSUE,
                date_from=date_from,
                date_to=date_to,
                access_token=access_token,
                page_offset=offset,
                page_size=self._PAGE_SIZE,
            )
            yield from response.invoices

            if not response.has_more:
                return
            offset += len(response.invoices)

        logger.warning(
            "KSeF invoice metadata pagination hit the safety limit (%s pages)",
            self._MAX_PAGES,
        )
