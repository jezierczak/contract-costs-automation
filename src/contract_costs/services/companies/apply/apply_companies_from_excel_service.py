from uuid import UUID

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.model.company import Address, BankAccount, CompanyType, Contact
from contract_costs.services.common.resolve_utils import normalize_required_tax_number
from contract_costs.services.companies.activate_company_service import ActivateCompanyService
from contract_costs.services.companies.apply.command import (
    ApplyCompaniesCommand,
    ApplyCompanyCommand,
    CompanyActionType,
)
from contract_costs.services.companies.create_company_service import CreateCompanyService
from contract_costs.services.companies.deactivate_company_service import DeactivateCompanyService
from contract_costs.services.companies.dto.activate_company_command import BaseActivateCompanyCommand
from contract_costs.services.companies.dto.create_company_command import (
    CreateCounterpartyCompanyCommand,
    CreateOwnerCompanyCommand,
)
from contract_costs.services.companies.dto.deactivate_company_command import BaseDeactivateCompanyCommand
from contract_costs.services.companies.dto.update_company_command import (
    UpdateCounterpartyCompanyCommand,
    UpdateOwnerCompanyCommand,
)
from contract_costs.services.companies.update_company_service import UpdateCompanyService
from contract_costs.unit_of_work import UnitOfWork


class ApplyCompaniesFromExcelService(ActionHandler[ApplyCompaniesCommand, None]):

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

    def execute(self, *, action: ApplyCompaniesCommand, uow: UnitOfWork) -> None:
        for idx, row_action in enumerate(action.commands, start=1):
            try:
                self._validate_batch_context(
                    batch_organization_id=action.organization_id,
                    batch_actor_user_id=action.actor_user_id,
                    row_action=row_action,
                )
                self._apply_action(
                    organization_id=action.organization_id,
                    actor_user_id=action.actor_user_id,
                    row_action=row_action,
                    uow=uow,
                )
            except Exception as exc:
                raise RuntimeError(f"Apply companies failed at command #{idx}: {row_action}") from exc

    @staticmethod
    def _validate_batch_context(
        *,
        batch_organization_id: UUID,
        batch_actor_user_id: UUID,
        row_action: ApplyCompanyCommand,
    ) -> None:
        if row_action.organization_id != batch_organization_id:
            raise ValueError(
                "Row command organization_id does not match batch organization_id"
            )
        if row_action.actor_user_id != batch_actor_user_id:
            raise ValueError(
                "Row command actor_user_id does not match batch actor_user_id"
            )

    def _apply_action(
        self,
        *,
        organization_id: UUID,
        actor_user_id: UUID,
        row_action: ApplyCompanyCommand,
        uow: UnitOfWork,
    ) -> None:
        action_type = row_action.apply_action_type

        if action_type == CompanyActionType.NONE:
            return
        if action_type == CompanyActionType.CREATE:
            self._handle_create(organization_id=organization_id, actor_user_id=actor_user_id, action=row_action, uow=uow)
            return
        if action_type == CompanyActionType.UPDATE:
            self._handle_update(organization_id=organization_id, actor_user_id=actor_user_id, action=row_action, uow=uow)
            return
        if action_type == CompanyActionType.ACTIVATE:
            self._handle_activate(organization_id=organization_id, actor_user_id=actor_user_id, action=row_action, uow=uow)
            return
        if action_type == CompanyActionType.DEACTIVATE:
            self._handle_deactivate(organization_id=organization_id, actor_user_id=actor_user_id, action=row_action, uow=uow)
            return

        raise ValueError(f"Unsupported company action: {action_type}")

    def _handle_create(
        self,
        *,
        organization_id: UUID,
        actor_user_id: UUID,
        action: ApplyCompanyCommand,
        uow: UnitOfWork,
    ) -> None:
        tax_number = normalize_required_tax_number(action.tax_number)
        create_cmd_type = CreateOwnerCompanyCommand if action.role == CompanyType.OWN else CreateCounterpartyCompanyCommand

        create_cmd = create_cmd_type(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            name=action.name,
            tax_number=tax_number,
            role=action.role,
            description=action.description,
            address=self._build_address(action),
            contact=self._build_contact(action),
            bank_account=self._build_bank_account(action),
            tags=action.tags,
        )

        self._create.execute(action=create_cmd, uow=uow)

    def _handle_update(
        self,
        *,
        organization_id: UUID,
        actor_user_id: UUID,
        action: ApplyCompanyCommand,
        uow: UnitOfWork,
    ) -> None:
        if not action.company_id:
            raise ValueError("UPDATE requires company_id")

        update_cmd_type = UpdateOwnerCompanyCommand if action.role == CompanyType.OWN else UpdateCounterpartyCompanyCommand

        update_cmd = update_cmd_type(
            organization_id=organization_id,
            company_id=action.company_id,
            actor_user_id=actor_user_id,
            name=action.name,
            role=action.role,
            address=self._build_address(action),
            contact=self._build_contact(action),
            description=action.description,
            tax_number=(normalize_required_tax_number(action.tax_number) if action.tax_number else None),
            bank_account=self._build_bank_account(action),
            tags=action.tags,
        )

        self._update.execute(action=update_cmd, uow=uow)

    def _handle_activate(
        self,
        *,
        organization_id: UUID,
        actor_user_id: UUID,
        action: ApplyCompanyCommand,
        uow: UnitOfWork,
    ) -> None:
        if not action.company_id:
            raise ValueError("ACTIVATE requires company_id")

        activate_cmd = BaseActivateCompanyCommand(
            organization_id=organization_id,
            company_id=action.company_id,
            actor_user_id=actor_user_id,
        )

        self._activate.execute(action=activate_cmd, uow=uow)

    def _handle_deactivate(
        self,
        *,
        organization_id: UUID,
        actor_user_id: UUID,
        action: ApplyCompanyCommand,
        uow: UnitOfWork,
    ) -> None:
        if not action.company_id:
            raise ValueError("DEACTIVATE requires company_id")

        deactivate_cmd = BaseDeactivateCompanyCommand(
            organization_id=organization_id,
            company_id=action.company_id,
            actor_user_id=actor_user_id,
        )

        self._deactivate.execute(action=deactivate_cmd, uow=uow)

    @staticmethod
    def _build_address(action: ApplyCompanyCommand) -> Address:
        return Address(
            street=action.address_street,
            city=action.address_city,
            zip_code=action.address_zip_code,
            country=action.address_country,
        )

    @staticmethod
    def _build_contact(action: ApplyCompanyCommand) -> Contact:
        return Contact(
            phone_number=action.phone_number,
            email=action.email,
        )

    @staticmethod
    def _build_bank_account(action: ApplyCompanyCommand) -> BankAccount | None:
        if not action.bank_account_number:
            return None
        return BankAccount(
            account_number=action.bank_account_number,
            country_code=action.bank_account_country_code,
        )
