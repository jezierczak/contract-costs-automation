import os
from uuid import uuid4

import pytest

import contract_costs.config as cfg
from contract_costs.services.documents.migration.repair_document_paths_command import (
    RepairDocumentPathsCommand,
)
from contract_costs.services.documents.migration.repair_document_paths_service import (
    PathFixKind,
    RepairDocumentPathsService,
    windows_safe_path,
)
from tests.builders.document_builder import DocumentBuilder

ORG = uuid4()
DOTTED = "owners/REMONTIVO_SP._Z_O.O./costs/invoices/2026/09/ONNIN_1_abc.xml"
FIXED = "owners/REMONTIVO_SP._Z_O.O/costs/invoices/2026/09/ONNIN_1_abc.xml"


@pytest.fixture
def org_root(tmp_path, monkeypatch):
    monkeypatch.setattr(cfg, "WORK_DIR", tmp_path)
    root = tmp_path / str(ORG)
    root.mkdir()
    return root


def _add(uow, file_path):
    document = (
        DocumentBuilder()
        .with_organization_id(ORG)
        .with_file_path(file_path)
        .with_filename(file_path.split("/")[-1])
        .build()
    )
    uow.documents.add(document)
    return document


def _run(uow, apply):
    return RepairDocumentPathsService().execute(
        action=RepairDocumentPathsCommand(organization_id=ORG, actor_user_id=uuid4(), apply=apply),
        uow=uow,
    )


def _write(root, relative):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("<x/>", encoding="utf-8")


def test_windows_safe_path_strips_trailing_dots_and_spaces_per_segment():
    assert windows_safe_path(DOTTED) == FIXED
    assert windows_safe_path("owners/A. /b.pdf") == "owners/A/b.pdf"
    assert windows_safe_path("incoming/x.pdf") == "incoming/x.pdf"


def test_dry_run_reports_without_changing_anything(uow, org_root):
    _write(org_root, FIXED)
    document = _add(uow, DOTTED)
    _add(uow, "incoming/ok.pdf")

    [fix] = _run(uow, apply=False)

    assert fix.kind == PathFixKind.PATH_ONLY
    assert fix.new_path == FIXED
    assert uow.documents.get(organization_id=ORG, document_id=document.id).file_path == DOTTED


def test_apply_updates_path_when_file_already_at_fixed_location(uow, org_root):
    _write(org_root, FIXED)
    document = _add(uow, DOTTED)

    _run(uow, apply=True)

    assert uow.documents.get(organization_id=ORG, document_id=document.id).file_path == FIXED
    assert _run(uow, apply=False) == []


def test_missing_file_is_reported_and_left_alone(uow, org_root):
    document = _add(uow, DOTTED)

    [fix] = _run(uow, apply=True)

    assert fix.kind == PathFixKind.MISSING
    assert uow.documents.get(organization_id=ORG, document_id=document.id).file_path == DOTTED


@pytest.mark.skipif(os.name == "nt", reason="Windows cannot create a directory ending with a dot")
def test_apply_moves_file_from_dotted_directory(uow, org_root):
    _write(org_root, DOTTED)
    document = _add(uow, DOTTED)

    [fix] = _run(uow, apply=True)

    assert fix.kind == PathFixKind.MOVE
    assert (org_root / FIXED).is_file()
    assert not (org_root / DOTTED).exists()
    assert uow.documents.get(organization_id=ORG, document_id=document.id).file_path == FIXED
