from uuid import UUID

from contract_costs.model.company import (
    Address,
    BankAccount,
    Contact,
)
from contract_costs.services.common.resolve_utils import (
    normalize_required_tax_number,
)
from contract_costs.services.companies.apply.command import (
    CompanyActionCommand,
    CompanyActionType,
)
from contract_costs.services.companies.create_company_service import (
    CreateCompanyService,
)
from contract_costs.services.companies.dto.activate_company_command import ActivateCompanyCommand
from contract_costs.services.companies.dto.create_company_command import CreateCompanyCommand
from contract_costs.services.companies.dto.deactivate_company_command import DeactivateCompanyCommand
from contract_costs.services.companies.dto.update_company_command import UpdateCompanyCommand
from contract_costs.services.companies.update_company_service import (
    UpdateCompanyService,
)
from contract_costs.services.companies.activate_company_service import (
    ActivateCompanyService,
)
from contract_costs.services.companies.deactivate_company_service import (
    DeactivateCompanyService,
)


class ApplyCompaniesFromExcelService:
    """
    Orchestrator command service.

    INPUT:
        list[CompanyActionCommand]

    RESPONSIBILITY:
        - execute create / update / activate / deactivate
        - no Excel logic
        - no Query logic
        - no DTO usage

    READY FOR:
        - Excel
        - CLI
        - API
    """

    def __init__(
        self,
        *,
        create_company_service: CreateCompanyService,
        update_company_service: UpdateCompanyService,
        activate_company_service: ActivateCompanyService,
        deactivate_company_service: DeactivateCompanyService,
    ) -> None:
        self._create = create_company_service
        self._update = update_company_service
        self._activate = activate_company_service
        self._deactivate = deactivate_company_service

    # =====================
    # PUBLIC API
    # =====================
    def apply(self,
              *,
              organization_id: UUID,
              actor_user_id: UUID,
              commands: list[CompanyActionCommand]
              ) -> None:
        for idx, command in enumerate(commands, start=1):
            try:
                self._apply_command(
                    organization_id=organization_id,
                    actor_user_id=actor_user_id,
                    cmd=command,
                )
            except Exception as exc:
                raise RuntimeError(
                    f"Apply companies failed at command #{idx}: {command}"
                ) from exc

    # =====================
    # COMMAND DISPATCH
    # =====================
    def _apply_command(    self,
                            *,
                            organization_id: UUID,
                            actor_user_id: UUID,
                            cmd: CompanyActionCommand
                           ) -> None:
        action = cmd.action

        if action == CompanyActionType.NONE:
            # explicit no-op
            return

        if action == CompanyActionType.CREATE:
            self._handle_create(organization_id=organization_id,
                                actor_user_id=actor_user_id,
                                cmd=cmd)
            return

        if action == CompanyActionType.UPDATE:
            self._handle_update(organization_id=organization_id,
                                actor_user_id=actor_user_id,
                                cmd=cmd)
            return

        if action == CompanyActionType.ACTIVATE:
            self._handle_activate(organization_id=organization_id,
                                actor_user_id=actor_user_id,
                                cmd=cmd)
            return

        if action == CompanyActionType.DEACTIVATE:
            self._handle_deactivate(organization_id=organization_id,
                                actor_user_id=actor_user_id,
                                cmd=cmd)
            return

        raise ValueError(f"Unsupported company action: {action}")

    # =====================
    # HANDLERS
    # =====================
    def _handle_create(
            self,
            *,
            organization_id: UUID,
            actor_user_id: UUID,
            cmd: CompanyActionCommand,
    ) -> None:
        tax_number = normalize_required_tax_number(cmd.tax_number)

        create_cmd = CreateCompanyCommand(
            organization_id=organization_id,
            actor_user_id=actor_user_id,

            name=cmd.name,
            tax_number=tax_number,
            role=cmd.role,

            description=cmd.description,
            address=self._build_address(cmd),
            contact=self._build_contact(cmd),
            bank_account=self._build_bank_account(cmd),
            tags=cmd.tags,
        )

        self._create.execute(create_cmd)

    def _handle_update(
            self,
            *,
            organization_id: UUID,
            actor_user_id: UUID,
            cmd: CompanyActionCommand,
    ) -> None:
        if not cmd.company_id:
            raise ValueError("UPDATE requires company_id")

        update_cmd = UpdateCompanyCommand(
            organization_id=organization_id,
            company_id=cmd.company_id,
            actor_user_id=actor_user_id,

            name=cmd.name,
            role=cmd.role,
            address=self._build_address(cmd),
            contact=self._build_contact(cmd),
            description=cmd.description,
            tax_number=(
                normalize_required_tax_number(cmd.tax_number)
                if cmd.tax_number
                else None
            ),
            bank_account=self._build_bank_account(cmd),
            tags=cmd.tags,
        )

        self._update.execute(update_cmd)

    def _handle_activate(
            self,
            *,
            organization_id: UUID,
            actor_user_id: UUID,
            cmd: CompanyActionCommand
            ) -> None:
        if not cmd.company_id:
            raise ValueError("ACTIVATE requires company_id")

        activate_cmd = ActivateCompanyCommand(
            organization_id=organization_id,
            company_id=cmd.company_id,
            actor_user_id=actor_user_id,
        )

        self._activate.execute(activate_cmd)

    def _handle_deactivate(  self,
            *,
            organization_id: UUID,
            actor_user_id: UUID,
            cmd: CompanyActionCommand
            ) -> None:
        if not cmd.company_id:
            raise ValueError("DEACTIVATE requires company_id")

        deactivate_cmd = DeactivateCompanyCommand(
            organization_id=organization_id,
            company_id=cmd.company_id,
            actor_user_id=actor_user_id,
        )

        self._deactivate.execute(deactivate_cmd)

    # =====================
    # BUILDERS
    # =====================
    @staticmethod
    def _build_address(cmd: CompanyActionCommand) -> Address:
        return Address(
            street=cmd.address_street,
            city=cmd.address_city,
            zip_code=cmd.address_zip_code,
            country=cmd.address_country,
        )

    @staticmethod
    def _build_contact(cmd: CompanyActionCommand) -> Contact:
        return Contact(
            phone_number=cmd.phone_number,
            email=cmd.email,
        )

    @staticmethod
    def _build_bank_account(cmd: CompanyActionCommand) -> BankAccount | None:
        if not cmd.bank_account_number:
            return None

        return BankAccount(
            account_number=cmd.bank_account_number,
            country_code=cmd.bank_account_country_code,
        )
