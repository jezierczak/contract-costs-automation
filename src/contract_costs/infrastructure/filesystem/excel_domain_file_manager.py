from datetime import datetime
from pathlib import Path
from uuid import UUID

import contract_costs.config as cfg



class ExcelDomainFileManager:
    """
     Zarządza lifecycle plików Excel dla domen:
     prepare / apply

     NIE zna domeny.
     NIE zna struktury Excela.
     """

    def __init__(
            self,
            *,
            organization_id: UUID,
            domain_dir: Path,
            domain_name: str,
    ) -> None:
        self._org_dir = cfg.WORK_DIR / str(organization_id)
        self._domain_dir = self._org_dir / domain_dir
        self._domain_name = domain_name

        self._active_file =  self._domain_dir / f"{domain_name}.xlsx"
        self._replaced_dir =  self._domain_dir / "replaced"
        self._processed_dir =  self._domain_dir / "processed"

        self._replaced_dir.mkdir(parents=True, exist_ok=True)
        self._processed_dir.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------
    # PREPARE
    # -------------------------------------------------

    def prepare_target(self) -> Path:
        """
        Zwraca ścieżkę, do której prepare MA zapisać nowy Excel.
        Jeśli istnieje aktywny plik → przenosi go do replaced/.
        """
        if self._active_file.exists():
            self._move_to_replaced()

        return self._active_file

    # -------------------------------------------------
    # APPLY
    # -------------------------------------------------

    def get_active_file(self) -> Path:
        """
        Zwraca aktywny plik roboczy.
        Rzuca wyjątek jeśli go nie ma.
        """
        if not self._active_file.exists():
            raise FileNotFoundError(
                f"No active Excel file for domain '{self._domain_name}'"
            )
        return self._active_file

    def mark_processed(self) -> Path:
        """
        Przenosi aktywny plik do processed/ po udanym apply.
        """
        if not self._active_file.exists():
            raise FileNotFoundError(
                f"No active Excel file to process for domain '{self._domain_name}'"
            )

        target = self._processed_dir / self._timestamped_name()
        self._active_file.replace(target)
        return target

    # -------------------------------------------------
    # INTERNALS
    # -------------------------------------------------

    def _move_to_replaced(self) -> None:
        target = self._replaced_dir / self._timestamped_name()
        self._active_file.replace(target)

    def _timestamped_name(self) -> str:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{self._domain_name}_{ts}.xlsx"


class FinancialRecordInvoiceAssignmentFileManager(ExcelDomainFileManager):
    def __init__(self,
                 *,
                 organization_id:UUID) -> None:
        path = cfg.INPUTS_INVOICES_ASSIGN_DIR
        name = cfg.INVOICES_INPUT_NAME
        super().__init__(
            organization_id=organization_id,
            domain_dir=Path(path),
            domain_name=name)


class DocumentAssignmentFileManager(ExcelDomainFileManager):
    def __init__(self,
                 *,
                 organization_id:UUID) -> None:
        path = cfg.INPUTS_DOCUMENTS_ASSIGN_DIR
        name = cfg.DOCUMENTS_INPUT_NAME
        super().__init__(
            organization_id=organization_id,
            domain_dir=Path(path),
            domain_name=name)

class InputsContractsAssignmentFileManager(ExcelDomainFileManager):
    def __init__(self,
                 *,
                 organization_id: UUID,
                 contract_code: str | None = None
                 ) -> None:
        path = cfg.INPUTS_CONTRACTS_DIR

        base_name = cfg.CONTRACT_EXCEL_NAME  # "contracts"
        name = (
            f"{base_name}_{contract_code}"
            if contract_code
            else base_name
        )

        super().__init__(
            organization_id=organization_id,
            domain_dir=Path(path),
            domain_name=name)

class InputsContractsProgressFileManager(ExcelDomainFileManager):
    def __init__(self,
                 *,
                 organization_id: UUID,
                 contract_code: str) -> None:
        path = cfg.INPUTS_CONTRACTS_DIR

        base_name = cfg.CONTRACT_PROGRESS_EXCEL_NAME  # np. "contract_progress"
        name = f"{base_name}_{contract_code}"

        super().__init__(
            organization_id=organization_id,
            domain_dir=Path(path),
            domain_name=name)


class InputsCompaniesAssignmentFileManager(ExcelDomainFileManager):
    def __init__(self,
                 *,
                 organization_id: UUID,
                 ) -> None:
        path = cfg.INPUTS_COMPANIES_DIR
        name = cfg.COMPANY_EXCEL_NAME
        super().__init__(
            organization_id=organization_id,
            domain_dir=Path(path),
            domain_name=name)



class FinancialRecordExcelPrepareFileManager(ExcelDomainFileManager):

    def __init__(self,
                 *,
                 organization_id: UUID,
                 view,
                 query
                 ):
        base_dir = cfg.INPUTS_INVOICES_DIR / view.value

        name = self._build_name(view, query)
        super().__init__(
            organization_id=organization_id,
            domain_dir=base_dir,
            domain_name=name)

    @staticmethod
    def _build_name(view, query) -> str:
        parts = [f"invoices_{view.value}"]

        if query.from_date or query.to_date:
            parts.append(
                f"{query.from_date or 'start'}_{query.to_date or 'end'}"
            )

        return "_".join(parts).lower()

