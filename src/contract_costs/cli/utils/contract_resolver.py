from uuid import UUID


def resolve_contract(contract_ref: str, services):
    repo = services.contract_repository

    try:
        contract = repo.get(UUID(contract_ref))
        if contract:
            return contract
    except ValueError:
        pass

    contract = repo.get_by_code(contract_ref)
    if contract:
        return contract

    raise RuntimeError(f"Contract not found: {contract_ref}")