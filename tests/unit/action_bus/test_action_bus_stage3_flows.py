from datetime import date
from uuid import uuid4

import pytest

from contract_costs.action_bus.action_bus import ActionBus
from contract_costs.action_bus.permission_resolver import PermissionResolver
from contract_costs.action_bus.permission_validator import PermissionValidator
from contract_costs.model.company import CompanyType
from contract_costs.model.financial_record import FinancialRecordStatus, PaymentStatus
from contract_costs.services.companies.apply.command import (
    ApplyCompaniesCommand,
    ApplyCompanyCommand,
    CompanyActionType,
)
from contract_costs.services.financial_records.actions.dto.invoice_action_command import (
    FinancialRecordAction,
    FinancialRecordActionCommand,
    FinancialRecordSelector,
)
from tests.builders.company_builder import CompanyBuilder
from tests.builders.financial_record_builder import FinancialRecordBuilder


class _AllowAllResolver(PermissionResolver):
    def has_permission(self, *, organization_id, user_id, action_type) -> bool:
        return True


def _bus_for_uow(uow):
    validator = PermissionValidator(permission_resolver=_AllowAllResolver())
    return ActionBus(permission_validator=validator, uow_factory=lambda: uow)


def test_action_bus_apply_companies_command_runs_all_mutations(services_memory, uow):
    org_id = uuid4()
    user_id = uuid4()
    bus = _bus_for_uow(uow)

    created_to_update = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_role(CompanyType.SUPPLIER)
        .with_tax_number("6792740424")
        .with_name("Old Supplier")
        .build()
    )
    inactive_to_activate = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_role(CompanyType.SUPPLIER)
        .with_tax_number("1132568413")
        .with_name("Inactive Supplier")
        .with_is_active(False)
        .build()
    )
    active_to_deactivate = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_role(CompanyType.SUPPLIER)
        .with_tax_number("6321001207")
        .with_name("Active Supplier")
        .with_is_active(True)
        .build()
    )
    uow.companies.add(created_to_update)
    uow.companies.add(inactive_to_activate)
    uow.companies.add(active_to_deactivate)

    bus.execute(
        action=ApplyCompaniesCommand(
            organization_id=org_id,
            actor_user_id=user_id,
            commands=[
                ApplyCompanyCommand(
                    organization_id=org_id,
                    actor_user_id=user_id,
                    apply_action_type=CompanyActionType.CREATE,
                    company_id=None,
                    tax_number="6762680195",
                    name="Created Supplier",
                    role=CompanyType.SUPPLIER,
                    description="new",
                    address_street=None,
                    address_city=None,
                    address_zip_code=None,
                    address_country=None,
                    phone_number=None,
                    email=None,
                    bank_account_number=None,
                    bank_account_country_code=None,
                    tags={"created"},
                ),
                ApplyCompanyCommand(
                    organization_id=org_id,
                    actor_user_id=user_id,
                    apply_action_type=CompanyActionType.UPDATE,
                    company_id=created_to_update.id,
                    tax_number=created_to_update.tax_number,
                    name="Updated Supplier",
                    role=CompanyType.SUPPLIER,
                    description=created_to_update.description,
                    address_street=None,
                    address_city=None,
                    address_zip_code=None,
                    address_country=None,
                    phone_number=None,
                    email=None,
                    bank_account_number=None,
                    bank_account_country_code=None,
                    tags=set(),
                ),
                ApplyCompanyCommand(
                    organization_id=org_id,
                    actor_user_id=user_id,
                    apply_action_type=CompanyActionType.ACTIVATE,
                    company_id=inactive_to_activate.id,
                    tax_number=inactive_to_activate.tax_number,
                    name=inactive_to_activate.name,
                    role=inactive_to_activate.role,
                    description=inactive_to_activate.description,
                    address_street=None,
                    address_city=None,
                    address_zip_code=None,
                    address_country=None,
                    phone_number=None,
                    email=None,
                    bank_account_number=None,
                    bank_account_country_code=None,
                    tags=set(),
                ),
                ApplyCompanyCommand(
                    organization_id=org_id,
                    actor_user_id=user_id,
                    apply_action_type=CompanyActionType.DEACTIVATE,
                    company_id=active_to_deactivate.id,
                    tax_number=active_to_deactivate.tax_number,
                    name=active_to_deactivate.name,
                    role=active_to_deactivate.role,
                    description=active_to_deactivate.description,
                    address_street=None,
                    address_city=None,
                    address_zip_code=None,
                    address_country=None,
                    phone_number=None,
                    email=None,
                    bank_account_number=None,
                    bank_account_country_code=None,
                    tags=set(),
                ),
            ],
        ),
        handler=services_memory.apply_companies_from_excel_service,
    )

    created = [
        c for c in uow.companies.list_all(organization_id=org_id) if c.tax_number == "6762680195"
    ]
    assert len(created) == 1
    assert created[0].name == "Created Supplier"

    updated = uow.companies.get(created_to_update.id, org_id)
    assert updated is not None
    assert updated.name == "Updated Supplier"

    activated = uow.companies.get(inactive_to_activate.id, org_id)
    assert activated is not None
    assert activated.is_active is True

    deactivated = uow.companies.get(active_to_deactivate.id, org_id)
    assert deactivated is not None
    assert deactivated.is_active is False


def test_action_bus_financial_record_mark_unpaid_sets_unpaid(services_memory, uow):
    org_id = uuid4()
    user_id = uuid4()
    bus = _bus_for_uow(uow)

    record = (
        FinancialRecordBuilder()
        .with_organization_id(org_id)
        .with_reference("UNPAID-1")
        .with_payment_status(PaymentStatus.PAID)
        .with_paid_date(date(2026, 2, 16))
        .build()
    )
    uow.financial_records.add(record)

    bus.execute(
        action=FinancialRecordActionCommand(
            organization_id=org_id,
            actor_user_id=user_id,
            action=FinancialRecordAction.MARK_UNPAID,
            selectors=[FinancialRecordSelector(record_reference="UNPAID-1")],
            payload=None,
        ),
        handler=services_memory.financial_record_action_service,
    )

    updated = uow.financial_records.get(organization_id=org_id, record_id=record.id)
    assert updated is not None
    assert updated.payment_status == PaymentStatus.UNPAID
    assert updated.paid_date is None


def test_action_bus_financial_record_mark_sent_to_accountant_on_processed(services_memory, uow):
    org_id = uuid4()
    user_id = uuid4()
    bus = _bus_for_uow(uow)

    record = (
        FinancialRecordBuilder()
        .with_organization_id(org_id)
        .with_reference("ACC-1")
        .with_status(FinancialRecordStatus.PROCESSED)
        .build()
    )
    uow.financial_records.add(record)

    bus.execute(
        action=FinancialRecordActionCommand(
            organization_id=org_id,
            actor_user_id=user_id,
            action=FinancialRecordAction.MARK_SENT_TO_ACCOUNTANT,
            selectors=[FinancialRecordSelector(record_reference="ACC-1")],
            payload=None,
        ),
        handler=services_memory.financial_record_action_service,
    )

    updated = uow.financial_records.get(organization_id=org_id, record_id=record.id)
    assert updated is not None
    assert updated.status == FinancialRecordStatus.SENT_TO_ACCOUNTANT


def test_action_bus_financial_record_reopen_sets_in_progress(services_memory, uow):
    org_id = uuid4()
    user_id = uuid4()
    bus = _bus_for_uow(uow)

    record = (
        FinancialRecordBuilder()
        .with_organization_id(org_id)
        .with_reference("REOPEN-1")
        .with_status(FinancialRecordStatus.SENT_TO_ACCOUNTANT)
        .build()
    )
    uow.financial_records.add(record)

    bus.execute(
        action=FinancialRecordActionCommand(
            organization_id=org_id,
            actor_user_id=user_id,
            action=FinancialRecordAction.REOPEN,
            selectors=[FinancialRecordSelector(record_reference="REOPEN-1")],
            payload=None,
        ),
        handler=services_memory.financial_record_action_service,
    )

    updated = uow.financial_records.get(organization_id=org_id, record_id=record.id)
    assert updated is not None
    assert updated.status == FinancialRecordStatus.IN_PROGRESS


def test_action_bus_apply_companies_command_rejects_row_with_different_organization_id(
    services_memory, uow
):
    org_id = uuid4()
    user_id = uuid4()
    bus = _bus_for_uow(uow)

    with_exception_org_id = uuid4()
    action = ApplyCompaniesCommand(
        organization_id=org_id,
        actor_user_id=user_id,
        commands=[
            ApplyCompanyCommand(
                organization_id=with_exception_org_id,
                actor_user_id=user_id,
                apply_action_type=CompanyActionType.CREATE,
                company_id=None,
                tax_number="6762680195",
                name="Supplier X",
                role=CompanyType.SUPPLIER,
                description=None,
                address_street=None,
                address_city=None,
                address_zip_code=None,
                address_country=None,
                phone_number=None,
                email=None,
                bank_account_number=None,
                bank_account_country_code=None,
                tags=set(),
            )
        ],
    )

    with pytest.raises(RuntimeError) as exc:
        bus.execute(action=action, handler=services_memory.apply_companies_from_excel_service)
    assert exc.value.__cause__ is not None
    assert "organization_id does not match batch organization_id" in str(exc.value.__cause__)


def test_action_bus_apply_companies_command_rejects_row_with_different_actor_user_id(
    services_memory, uow
):
    org_id = uuid4()
    user_id = uuid4()
    bus = _bus_for_uow(uow)

    with_exception_user_id = uuid4()
    action = ApplyCompaniesCommand(
        organization_id=org_id,
        actor_user_id=user_id,
        commands=[
            ApplyCompanyCommand(
                organization_id=org_id,
                actor_user_id=with_exception_user_id,
                apply_action_type=CompanyActionType.CREATE,
                company_id=None,
                tax_number="6762680195",
                name="Supplier X",
                role=CompanyType.SUPPLIER,
                description=None,
                address_street=None,
                address_city=None,
                address_zip_code=None,
                address_country=None,
                phone_number=None,
                email=None,
                bank_account_number=None,
                bank_account_country_code=None,
                tags=set(),
            )
        ],
    )

    with pytest.raises(RuntimeError) as exc:
        bus.execute(action=action, handler=services_memory.apply_companies_from_excel_service)
    assert exc.value.__cause__ is not None
    assert "actor_user_id does not match batch actor_user_id" in str(exc.value.__cause__)
