from riemann.database import DivisorDb
from riemann.database import RiemannDivisorSum
from riemann.database import SummaryStats
from riemann.in_memory_database import InMemoryDivisorDb
import pytest

newDatabase = InMemoryDivisorDb


def test_initially_empty():
    db: DivisorDb = newDatabase()
    assert len(db.load()) == 0


def test_upsert_from_empty():
    db: DivisorDb = newDatabase()
    records = [
        RiemannDivisorSum(n=1, divisor_sum=1, witness_value=1),
        RiemannDivisorSum(n=2, divisor_sum=2, witness_value=2),
    ]

    db.upsert(records)
    assert set(db.load()) == set(records)


def test_upsert_from_nonempty():
    db: DivisorDb = newDatabase()
    records = [
        RiemannDivisorSum(n=1, divisor_sum=1, witness_value=1),
        RiemannDivisorSum(n=2, divisor_sum=2, witness_value=2),
    ]
    db.upsert(records)

    new_records = [
        RiemannDivisorSum(n=3, divisor_sum=3, witness_value=3),
        RiemannDivisorSum(n=4, divisor_sum=4, witness_value=4),
    ]
    db.upsert(new_records)

    assert set(db.load()) == set(records + new_records)


def test_upsert_overrides():
    db: DivisorDb = newDatabase()
    records = [
        RiemannDivisorSum(n=1, divisor_sum=1, witness_value=1),
        RiemannDivisorSum(n=2, divisor_sum=2, witness_value=2),
    ]
    db.upsert(records)

    new_records = [
        RiemannDivisorSum(n=1, divisor_sum=3, witness_value=3),
        RiemannDivisorSum(n=4, divisor_sum=4, witness_value=4),
    ]
    db.upsert(new_records)

    assert set(db.load()) == set([records[1]] + new_records)


def test_summarize_empty():
    db: DivisorDb = newDatabase()
    expected = SummaryStats(largest_computed_n=None,
                            largest_witness_value=None)

    assert expected == db.summarize()


def test_summarize_nonempty():
    db: DivisorDb = newDatabase()
    records = [
        RiemannDivisorSum(n=9, divisor_sum=3, witness_value=3),
        RiemannDivisorSum(n=4, divisor_sum=4, witness_value=4),
    ]
    db.upsert(records)
    expected = SummaryStats(largest_computed_n=records[0],
                            largest_witness_value=records[1])

    assert expected == db.summarize()
