from datetime import date

from contract_costs.services.ksef.ksef_api_client import KsefApiClient


def test_iter_date_chunks_splits_long_range_at_100_days():
    chunks = list(KsefApiClient._iter_date_chunks(date(2026, 1, 1), date(2026, 9, 22)))

    assert chunks == [
        (date(2026, 1, 1), date(2026, 4, 11)),
        (date(2026, 4, 12), date(2026, 7, 21)),
        (date(2026, 7, 22), date(2026, 9, 22)),
    ]
    for start, end in chunks:
        assert (end - start).days <= 100

    # kolejne kawałki muszą się stykać bez dziury i bez nakładania
    for (_, prev_end), (next_start, _) in zip(chunks, chunks[1:]):
        assert (next_start - prev_end).days == 1


def test_iter_date_chunks_single_chunk_when_within_limit():
    chunks = list(KsefApiClient._iter_date_chunks(date(2026, 1, 1), date(2026, 1, 10)))

    assert chunks == [(date(2026, 1, 1), date(2026, 1, 10))]


def test_iter_date_chunks_same_day_range():
    chunks = list(KsefApiClient._iter_date_chunks(date(2026, 1, 1), date(2026, 1, 1)))

    assert chunks == [(date(2026, 1, 1), date(2026, 1, 1))]
