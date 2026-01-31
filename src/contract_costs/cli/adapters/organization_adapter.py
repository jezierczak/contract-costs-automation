from contract_costs.services.identity.add.dto.create_organization_command import (
    CreateOrganizationCommand,
)


def create_organization_from_cli(
    *,
    data: dict,
    create_organization_service,
) -> None:
    cmd = CreateOrganizationCommand(
        organization_code=data["organization_code"],
        organization_name=data["organization_name"],
        owner_login=data["owner_login"],
        owner_email=data.get("owner_email"),
        owner_full_name=data.get("owner_full_name"),
        created_by_user_id=None,  # CLI = system / bootstrap
    )

    create_organization_service.execute(cmd)
