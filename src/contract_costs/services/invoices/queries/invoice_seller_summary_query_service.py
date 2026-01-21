from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from contract_costs.repository.invoice_repository import InvoiceRepository
from contract_costs.repository.invoice_line_repository import InvoiceLineRepository
from contract_costs.repository.company_repository import CompanyRepository
from contract_costs.model.invoice import InvoiceStatus


@dataclass(frozen=True)
class SellerInvoiceSummaryRow:
    invoice_number: str
    invoice_date: str | None
    status: InvoiceStatus
    net: Decimal
    vat: Decimal
    gross: Decimal
    paid: bool


@dataclass(frozen=True)
class SellerInvoiceSummary:
    seller_name: str
    seller_tax_number: str
    invoices: list[SellerInvoiceSummaryRow]
    total_net: Decimal
    total_vat: Decimal
    total_gross: Decimal


class InvoiceSellerSummaryQueryService:
    def __init__(
        self,
        invoice_repo: InvoiceRepository,
        invoice_line_repo: InvoiceLineRepository,
        company_repo: CompanyRepository,
    ):
        self._invoice_repo = invoice_repo
        self._line_repo = invoice_line_repo
        self._company_repo = company_repo

    def get_by_seller_nip(self, tax_number: str) -> SellerInvoiceSummary:
        seller = self._company_repo.get_by_tax_number(tax_number)
        if not seller:
            raise RuntimeError(f"Seller not found for NIP {tax_number}")

        invoices = self._invoice_repo.list_by_seller_id(seller.id)

        rows: list[SellerInvoiceSummaryRow] = []

        total_net = Decimal("0.00")
        total_vat = Decimal("0.00")
        total_gross = Decimal("0.00")

        invoices.sort(key=lambda x: x.invoice_date or date.min, reverse=True)

        for inv in invoices:
            if inv.status != InvoiceStatus.PROCESSED:
                continue
            lines = self._line_repo.list_by_invoice_ids([inv.id])
            net = sum((l.amount.net for l in lines),Decimal("0.00"))
            vat = sum((l.amount.tax for l in lines),Decimal("0.00"))
            gross = sum((l.amount.gross for l in lines),Decimal("0.00"))

            total_net += net
            total_vat += vat
            total_gross += gross

            rows.append(
                SellerInvoiceSummaryRow(
                    invoice_number=inv.invoice_number,
                    invoice_date=str(inv.invoice_date) if inv.invoice_date else None,
                    status=inv.status,
                    net = net,
                    vat=vat,
                    gross=gross,
                    paid=inv.payment_status.name == "PAID",
                )
            )

        return SellerInvoiceSummary(
            seller_name=seller.name,
            seller_tax_number=seller.tax_number,
            invoices=rows,
            total_net=total_net,
            total_vat=total_vat,
            total_gross=total_gross,
        )
