from datetime import datetime

import pytest
import testing.postgresql
from gmpy2 import mpz
from riemann.database import DivisorDb
from riemann.database import SearchMetadataDb
from riemann.in_memory_database import InMemoryDivisorDb
from riemann.postgres_database import PostgresDivisorDb
from riemann.sqlite_database import SqliteDivisorDb
from riemann.types import ExhaustiveSearchIndex
from riemann.types import RiemannDivisorSum
from riemann.types import SearchMetadata
from riemann.types import SummaryStats


def noop_teardown():
    pass


def createSqliteDb():
    db = SqliteDivisorDb(database_path=":memory:")
    db.initialize_schema()
    db.teardown = noop_teardown
    return db


def createInMemoryDb():
    db = InMemoryDivisorDb()
    db.teardown = noop_teardown
    return db


def createPostgresDb():
    tmp_postgres = testing.postgresql.Postgresql()
    db = PostgresDivisorDb(data_source_dict=tmp_postgres.dsn())
    db.initialize_schema()
    db.teardown = tmp_postgres.stop
    return db


@pytest.mark.parametrize('newDatabase',
                         [createInMemoryDb, createSqliteDb, createPostgresDb])
class TestDatabase:
    def test_initially_empty(self, newDatabase):
        db: DivisorDb = newDatabase()
        assert len(db.load()) == 0
        db.teardown()

    def test_upsert_from_empty(self, newDatabase):
        db: DivisorDb = newDatabase()
        records = [
            RiemannDivisorSum(n=1, divisor_sum=1, witness_value=1),
            RiemannDivisorSum(n=2, divisor_sum=2, witness_value=2),
        ]

        db.upsert(records)
        assert set(db.load()) == set(records)
        db.teardown()

    def test_upsert_mpz(self, newDatabase):
        db: DivisorDb = newDatabase()
        records = [
            RiemannDivisorSum(n=mpz(1), divisor_sum=mpz(1), witness_value=1),
        ]

        db.upsert(records)
        assert set(db.load()) == set(records)
        db.teardown()

    def test_upsert_from_nonempty(self, newDatabase):
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
        db.teardown()

    def test_upsert_overrides(self, newDatabase):
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
        db.teardown()

    def test_summarize_empty(self, newDatabase):
        db: DivisorDb = newDatabase()
        expected = SummaryStats(largest_computed_n=None,
                                largest_witness_value=None)

        assert expected == db.summarize()
        db.teardown()

    def test_summarize_nonempty(self, newDatabase):
        db: DivisorDb = newDatabase()
        records = [
            RiemannDivisorSum(n=9, divisor_sum=3, witness_value=3),
            RiemannDivisorSum(n=4, divisor_sum=4, witness_value=4),
        ]
        db.upsert(records)
        expected = SummaryStats(largest_computed_n=records[0],
                                largest_witness_value=records[1])

        assert expected == db.summarize()
        db.teardown()

    def test_fetch_empty_metadata(self, newDatabase):
        name = "ExhaustiveSearchIndex"
        db: SearchMetadataDb = newDatabase()
        assert db.latest_search_metadata(name) is None
        db.teardown()

    def test_store_metadata(self, newDatabase):
        name = "ExhaustiveSearchIndex"
        db: SearchMetadataDb = newDatabase()
        metadata = [
            SearchMetadata(start_time=datetime(2020, 9, 1, 0, 0, 0),
                           end_time=datetime(2020, 9, 1, 1, 0, 0),
                           search_state_type=name,
                           starting_search_state=ExhaustiveSearchIndex(n=1),
                           ending_search_state=ExhaustiveSearchIndex(n=2)),
        ]

        db.insert_search_metadata(metadata[0])
        assert metadata[0] == db.latest_search_metadata(name)
        db.teardown()

    def test_store_metadata_ordering(self, newDatabase):
        name = "ExhaustiveSearchIndex"
        db: SearchMetadataDb = newDatabase()
        older_time = datetime(2016, 9, 1, 1, 0, 0)
        newer_time = datetime(2020, 9, 1, 1, 0, 0)
        metadata = [
            SearchMetadata(start_time=older_time,
                           end_time=older_time,
                           search_state_type=name,
                           starting_search_state=ExhaustiveSearchIndex(n=1),
                           ending_search_state=ExhaustiveSearchIndex(n=2)),
            SearchMetadata(start_time=newer_time,
                           end_time=newer_time,
                           search_state_type=name,
                           starting_search_state=ExhaustiveSearchIndex(n=1),
                           ending_search_state=ExhaustiveSearchIndex(n=2)),
        ]

        # insert the newer one first
        db.insert_search_metadata(metadata[1])
        db.insert_search_metadata(metadata[0])
        assert metadata[1] == db.latest_search_metadata(name)
        db.teardown()
