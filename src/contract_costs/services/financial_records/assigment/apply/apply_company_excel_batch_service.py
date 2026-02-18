from dataclasses import replace
import logging

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.model.company import CompanyType
from contract_costs.services.companies.create_company_service import CreateCompanyService

from contract_costs.services.companies.dto.create_company_command import (
    CreateCounterpartyCompanyCommand,
)
from contract_costs.services.companies.normalize.normalize_service import CompanyNormalizeService
from contract_costs.services.financial_records.assigment.apply.commands.apply_company_excel_batch_command import \
    ApplyCompanyExcelBatchCommand

from contract_costs.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)


class ApplyCompanyExcelBatchService(
    ActionHandler[ApplyCompanyExcelBatchCommand, None]
):
    def __init__(self, create_company_service: CreateCompanyService):
        self._create_company_service = create_company_service
        self._normalizator= CompanyNormalizeService()

    def execute(
        self,
        *,
        action: ApplyCompanyExcelBatchCommand,
        uow: UnitOfWork,
    ) -> None:
        company_repo = uow.companies
        for c in action.companies:
            existing = company_repo.get(
                organization_id=action.organization_id,
                company_id=c.id,
            )

            normalized_tax = self._normalizator.normalize_tax_number(str(c.tax_number))
            if normalized_tax is None:
                raise ValueError(
                    f"Company from Excel must have valid tax_number. "
                    f"id={c.id}, name='{c.name}', tax_number='{c.tax_number}'"
                )
            nip_owner = company_repo.get_by_tax_number(
                organization_id=action.organization_id,
                tax_number=normalized_tax,
            )
            # case 1: „nie ma w repo takiego ID i nie ma tax number”
            if not existing and not nip_owner:
                logger.info(
                    "Creating new company from Excel: name='%s', tax_number='%s'",
                    c.name,
                    c.tax_number,
                )

                self._create_company_service.execute(
                    action=CreateCounterpartyCompanyCommand(
                        organization_id=action.organization_id,
                        actor_user_id=action.actor_user_id,
                        name=c.name,
                        tax_number=normalized_tax,
                        role=CompanyType.CLIENT,
                    ),
                    uow=uow
                )
                continue  # albo raise – decyzja biznesowa

            # nic się nie zmieniło
            if c and existing:
                if (
                            existing.name == c.name
                            and existing.tax_number == c.tax_number # llm zaproponował:and existing.tax_number == normalized_tax
                ):
                    continue


            # CASE 3: Excel zmienia NIP na taki, który już należy do innej firmy → MERGE
            if  existing and nip_owner and nip_owner.id != existing.id:
                logger.warning(
                    "Company NIP conflict (org=%s). "
                    "Merging: delete=%s keep=%s tax=%s",
                    action.organization_id,
                    existing.id,
                    nip_owner.id,
                    normalized_tax,
                )
                #  usuwamy "złą" firmę (tą aktualizowaną)

                company_repo.delete(
                    organization_id=action.organization_id,
                    company_id=existing.id,
                )

                #  aktualizujemy poprawną (bez id i nip)
                merged = replace(
                    nip_owner,
                    name=c.name,
                    # inne pola OK do nadpisania
                )
                company_repo.update(merged)

            # CASE 2: Excel zmienia NIP, brak konfliktu → UPDATE
            else:
                if existing:
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
                        tax_number=normalized_tax,
                    )
                    # print(updated)
                    company_repo.update(updated)
