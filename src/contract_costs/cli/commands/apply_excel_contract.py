from pathlib import Path
from datetime import datetime
from uuid import UUID

import contract_costs.config as cfg
from contract_costs.cli.context import get_services


def handle_applyexcel_contract(ref: str) -> None:

    if ref is None:
        print("Missing contract reference. Use 'new' or contract UUID/code.")
        return

    services = get_services()


    if ref == "new":
        _apply_new_contract(services)
    else:
        _apply_edit_contract(services, ref)


# ---------------- helpers ----------------

def _apply_new_contract(services) -> None:
    excel_path = _find_single_excel(cfg.INPUTS_CONTRACTS_NEW_DIR /
            cfg.CONTRACT_EXCEL_FILENAME)

    services.apply_contract_structure_excel.apply_new(excel_path)

    _move_to_processed(
        excel_path,
        cfg.INPUTS_CONTRACTS_PROCESSED_DIR / "new",
    )

    print("Contract created successfully from Excel.")


def _apply_edit_contract(services, ref: str) -> None:
    contract = _resolve_contract(ref, services.contract_repository)

    # filename = cfg.CONTRACT_EDIT_EXCEL_TEMPLATE.format(code=contract.code)
    excel_path = _find_single_excel(cfg.INPUTS_CONTRACTS_EDIT_DIR)

    services.apply_contract_structure_excel.apply_update(
        contract_id=contract.id,
        excel_path=excel_path,
    )

    _move_to_processed(
        excel_path,
        cfg.INPUTS_CONTRACTS_PROCESSED_DIR / "edit",
    )

    print(f"Contract {contract.code} updated successfully.")


def _find_single_excel(dir_path: Path) -> Path:
    files = list(dir_path.glob("*.xlsx"))

    if not files:
        raise RuntimeError(f"No Excel files found in {dir_path}")

    if len(files) > 1:
        raise RuntimeError(f"Multiple Excel files found in {dir_path}, expected exactly one")

    return files[0]


def _resolve_contract(ref: str, repo):
    try:
        contract_id = UUID(ref)
        contract = repo.get(contract_id)
    except ValueError:
        contract = repo.get_by_code(ref)

    if contract is None:
        raise RuntimeError(f"Contract not found: {ref}")

    return contract


def _move_to_processed(src: Path, base_dir: Path) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    target_dir = base_dir / timestamp
    target_dir.mkdir(parents=True, exist_ok=True)

    src.replace(target_dir / src.name)
