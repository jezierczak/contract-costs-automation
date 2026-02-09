from uuid import UUID


def resolve_contract(contract_ref: str, organization_id: UUID, services):
    repo = services.contract_repository

    try:
        contract = repo.get(organization_id,UUID(contract_ref))
        if contract:
            return contract
    except ValueError:
        pass

    contract = repo.get_by_code(organization_id,contract_ref)
    if contract:
        return contract

    raise RuntimeError(f"Contract not found: {contract_ref}")