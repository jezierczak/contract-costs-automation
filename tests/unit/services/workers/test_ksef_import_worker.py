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
