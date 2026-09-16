from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass(frozen=True, slots=True)
class KsefDownloadedInvoice:
    external_id: str
    filename: str
    xml_content: bytes


class KsefApiClient:
    """
    Lightweight KSeF client wrapper.

    Modes:
    - mock (default): reads XML files from KSEF_MOCK_XML_DIR
    - http: generic HTTP flow with configurable endpoints
    """

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
            return self._fetch_http(
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

    def _fetch_http(
        self,
        *,
        settings,
        company,
        from_date: date,
        to_date: date,
    ) -> list[KsefDownloadedInvoice]:
        token = os.getenv("KSEF_API_TOKEN")
        if not token:
            raise RuntimeError("KSEF_API_TOKEN is missing for KSEF_IMPORT_MODE=http")

        base_url = self._resolve_base_url(settings.environment.value)
        query_endpoint = os.getenv("KSEF_API_QUERY_ENDPOINT", "/invoices/query")
        download_endpoint = os.getenv("KSEF_API_DOWNLOAD_ENDPOINT", "/invoices/{invoice_id}/xml")

        query_url = f"{base_url.rstrip('/')}/{query_endpoint.lstrip('/')}"
        payload = {
            "sellerTaxNumber": company.tax_number,
            "fromDate": from_date.isoformat(),
            "toDate": to_date.isoformat(),
        }

        response = self._request_json(
            method="POST",
            url=query_url,
            token=token,
            body=payload,
        )

        invoices = response.get("items") or response.get("invoices") or []
        result: list[KsefDownloadedInvoice] = []
        for item in invoices:
            invoice_id = (
                item.get("id")
                or item.get("invoiceId")
                or item.get("ksefReferenceNumber")
            )
            if not invoice_id:
                continue

            dl_path = download_endpoint.replace("{invoice_id}", str(invoice_id))
            dl_url = f"{base_url.rstrip('/')}/{dl_path.lstrip('/')}"
            xml_content = self._request_bytes(
                method="GET",
                url=dl_url,
                token=token,
            )
            result.append(
                KsefDownloadedInvoice(
                    external_id=str(invoice_id),
                    filename=f"ksef_{company.tax_number}_{invoice_id}.xml",
                    xml_content=xml_content,
                )
            )
        return result

    @staticmethod
    def _resolve_base_url(environment: str) -> str:
        mapping = {
            "test": os.getenv("KSEF_BASE_URL_TEST", ""),
            "demo": os.getenv("KSEF_BASE_URL_DEMO", ""),
            "prod": os.getenv("KSEF_BASE_URL_PROD", ""),
        }
        base = mapping.get(environment)
        if not base:
            raise RuntimeError(f"Missing KSeF base URL for environment: {environment}")
        return base

    @staticmethod
    def _request_json(
        *,
        method: str,
        url: str,
        token: str,
        body: dict | None = None,
    ) -> dict:
        raw_body = json.dumps(body).encode("utf-8") if body is not None else None
        request = Request(url=url, data=raw_body, method=method)
        request.add_header("Authorization", f"Bearer {token}")
        request.add_header("Content-Type", "application/json")
        request.add_header("Accept", "application/json")
        try:
            with urlopen(request, timeout=60) as response:
                raw = response.read()
                if not raw:
                    return {}
                parsed = json.loads(raw.decode("utf-8"))
                if isinstance(parsed, dict):
                    return parsed
                return {"items": parsed}
        except HTTPError as exc:
            raise RuntimeError(f"KSeF HTTP error {exc.code}: {exc.reason}") from exc
        except URLError as exc:
            raise RuntimeError(f"KSeF connection error: {exc.reason}") from exc

    @staticmethod
    def _request_bytes(
        *,
        method: str,
        url: str,
        token: str,
    ) -> bytes:
        request = Request(url=url, method=method)
        request.add_header("Authorization", f"Bearer {token}")
        request.add_header("Accept", "application/xml")
        try:
            with urlopen(request, timeout=60) as response:
                return response.read()
        except HTTPError as exc:
            raise RuntimeError(f"KSeF download HTTP error {exc.code}: {exc.reason}") from exc
        except URLError as exc:
            raise RuntimeError(f"KSeF download connection error: {exc.reason}") from exc
