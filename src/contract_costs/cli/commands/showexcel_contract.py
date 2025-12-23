
import contract_costs.config as cfg
from uuid import UUID

from contract_costs.cli.context import get_services


def handle_showexcel_contract(contract_ref: str | None = None) -> None:
    services = get_services()

    output_path = (
            cfg.INPUTS_CONTRACTS_NEW_DIR /
            cfg.CONTRACT_EXCEL_FILENAME
    )

    service = services.generate_contract_structure_excel

    if contract_ref is None:
        service.generate_empty(output_path)
        print(f"Empty contract structure Excel generated: {output_path}")
        return

    # próbujemy UUID
    contract = None
    try:
        contract = services.contract_repository.get(UUID(contract_ref))
    except ValueError:
        pass

    # fallback: code
    if contract is None:
        contracts = services.contract_repository.list()
        contract = next(
            (c for c in contracts if c.code == contract_ref),
            None,
        )

    if contract is None:
        print("Contract not found.")
        return

    filename = cfg.CONTRACT_EDIT_EXCEL_TEMPLATE.format(code=contract.code)
    output_path = cfg.INPUTS_CONTRACTS_EDIT_DIR / filename

    service.generate_from_contract(contract.id, output_path)
    print(f"Contract structure Excel generated: {output_path}")
