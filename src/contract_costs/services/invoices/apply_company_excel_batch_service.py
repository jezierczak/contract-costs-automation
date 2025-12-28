from dataclasses import replace
import logging

from contract_costs.model.company import CompanyType
from contract_costs.repository.company_repository import CompanyRepository
from contract_costs.services.companies.create_company_service import CreateCompanyService
from contract_costs.services.invoices.dto.export.company_export import CompanyExport


logger = logging.getLogger(__name__)


class ApplyCompanyExcelBatchService:
    def __init__(self, company_repository: CompanyRepository):
        self._repo = company_repository
        self._create_company_service = CreateCompanyService(company_repository)

    def apply(self, companies: list[CompanyExport]) -> None:
        for c in companies:
            existing = self._repo.get(c.id)

            if not existing:
                if not self._repo.get_by_tax_number(c.tax_number):
                    logger.info(
                        "Creating new company from Excel: name='%s', tax_number='%s'",
                        c.name,
                        c.tax_number,
                    )
                    self._create_company_service.execute(
                        name=c.name,
                        tax_number=c.tax_number,
                        address=None,
                        contact=None,
                        role=CompanyType.CLIENT
                    )
                continue  # albo raise – decyzja biznesowa

            # nic się nie zmieniło
            if (
                    existing.name == c.name
                    and existing.tax_number == c.tax_number
            ):
                continue

            # 🔴 konflikt NIP
            nip_owner = self._repo.get_by_tax_number(c.tax_number)

            if nip_owner and nip_owner.id != existing.id:
                logger.warning(
                    "NIP conflict detected during Excel import. "
                    "Merging companies: source_id=%s deleted, target_id=%s kept, tax_number=%s",
                    existing.id,
                    nip_owner.id,
                    c.tax_number,
                )
                #  usuwamy "złą" firmę (tą aktualizowaną)
                self._repo.delete(existing.id)

                #  aktualizujemy poprawną (bez id i nip)
                merged = replace(
                    nip_owner,
                    name=c.name,
                    # inne pola OK do nadpisania
                )
                self._repo.update(merged)

            else:
                logger.info(
                    "Updating company from Excel: id=%s, name='%s', tax_number='%s'",
                    existing.id,
                    c.name,
                    c.tax_number,
                )
                #  normalny update (brak konfliktu)
                updated = replace(
                    existing,
                    name=c.name,
                    tax_number=c.tax_number,
                )
                self._repo.update(updated)