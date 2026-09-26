from datetime import date

from contract_costs.services.workers.ksef_import_worker import KsefImportWorker


def test_first_import_sets_marker_to_imported_end():
    assert KsefImportWorker._next_last_import_from(
        current=None, imported_to=date(2026, 9, 24)
    ) == date(2026, 9, 24)


def test_newer_import_moves_marker_forward():
    assert KsefImportWorker._next_last_import_from(
        current=date(2026, 9, 20), imported_to=date(2026, 9, 24)
    ) == date(2026, 9, 24)


def test_manual_import_of_older_period_does_not_move_marker_back():
    assert KsefImportWorker._next_last_import_from(
        current=date(2026, 9, 20), imported_to=date(2026, 1, 31)
    ) == date(2026, 9, 20)


def _stored_document(uow, ksef_number=None):
    from dataclasses import replace
    from uuid import uuid4

    from tests.builders.document_builder import DocumentBuilder

    document = replace(DocumentBuilder().with_organization_id(uuid4()).build(), ksef_number=ksef_number)
    uow.documents.add(document)
    return document


def _remember(uow, document, ksef_number):
    KsefImportWorker._remember_ksef_number(
        uow=uow,
        organization_id=document.organization_id,
        document_id=document.id,
        ksef_number=ksef_number,
    )
    return uow.documents.get(organization_id=document.organization_id, document_id=document.id)


def test_duplicate_import_fills_missing_ksef_number(uow):
    document = _stored_document(uow)

    assert _remember(uow, document, "1111111111-20260915-0100001AF629-AF").ksef_number == (
        "1111111111-20260915-0100001AF629-AF"
    )


def test_duplicate_import_keeps_existing_ksef_number(uow):
    document = _stored_document(uow, ksef_number="OLD")

    assert _remember(uow, document, "NEW").ksef_number == "OLD"
    assert _remember(uow, _stored_document(uow), None).ksef_number is None
