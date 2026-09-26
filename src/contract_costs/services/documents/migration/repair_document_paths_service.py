from dataclasses import dataclass, replace
from enum import Enum
from pathlib import Path
from uuid import UUID

import contract_costs.config as cfg
from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.services.documents.migration.repair_document_paths_command import (
    RepairDocumentPathsCommand,
)
from contract_costs.unit_of_work import UnitOfWork


class PathFixKind(Enum):
    PATH_ONLY = "path_only"  # plik już leży pod poprawną ścieżką – zmiana tylko w bazie
    MOVE = "move"            # plik leży pod starą ścieżką – przenieść i zmienić w bazie
    MISSING = "missing"      # pliku nie ma pod żadną ze ścieżek – do ręcznego sprawdzenia


@dataclass(frozen=True, slots=True)
class DocumentPathFix:
    document_id: UUID
    old_path: str
    new_path: str
    kind: PathFixKind


def windows_safe_path(relative_path: str) -> str:
    """Obcina kropki/spacje z końca każdego segmentu (Windows i tak je ignoruje)."""
    return "/".join(
        segment.rstrip(". ") or segment
        for segment in relative_path.replace("\\", "/").split("/")
    )


class RepairDocumentPathsService(
    ActionHandler[RepairDocumentPathsCommand, list[DocumentPathFix]]
):
    """
    Naprawa ścieżek dokumentów z segmentami kończącymi się kropką/spacją
    (np. owners/REMONTIVO_SP._Z_O.O./...). Na hoście Windows taki katalog
    „zlewa się” z wersją bez kropki, w kontenerze Linux jest osobnym katalogiem –
    pliki rozjechały się między nie. Docelowo wszystko ląduje w wersji bez kropki.
    Uruchamiać w kontenerze (tam widać oba katalogi).
    """

    def execute(
        self,
        *,
        action: RepairDocumentPathsCommand,
        uow: UnitOfWork,
    ) -> list[DocumentPathFix]:
        org_root = cfg.WORK_DIR / str(action.organization_id)
        fixes: list[DocumentPathFix] = []

        for document in uow.documents.list_filtered(organization_id=action.organization_id):
            if not document.file_path:
                continue
            old_path = Path(document.file_path).as_posix()
            new_path = windows_safe_path(old_path)
            if new_path == old_path:
                continue

            old_abs = org_root / old_path
            new_abs = org_root / new_path
            if new_abs.is_file():
                kind = PathFixKind.PATH_ONLY
            elif old_abs.is_file():
                kind = PathFixKind.MOVE
            else:
                kind = PathFixKind.MISSING

            fixes.append(DocumentPathFix(document.id, old_path, new_path, kind))

            if not action.apply or kind == PathFixKind.MISSING:
                continue

            if kind == PathFixKind.MOVE:
                new_abs.parent.mkdir(parents=True, exist_ok=True)
                old_abs.replace(new_abs)

            uow.documents.update(
                replace(document, file_path=new_path, filename=Path(new_path).name)
            )

        return fixes
