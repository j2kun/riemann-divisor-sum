from dataclasses import replace
from datetime import datetime
from gmpy2 import mpz
import pytest
import testing.postgresql

from riemann.database import DivisorDb
from riemann.in_memory_database import InMemoryDivisorDb
from riemann.postgres_database import PostgresDivisorDb
from riemann.types import ExhaustiveSearchIndex
from riemann.types import RiemannDivisorSum
from riemann.types import SearchBlockState
from riemann.types import SearchMetadata
from riemann.types import SummaryStats
from riemann.types import SuperabundantEnumerationIndex


def noop_teardown():
    pass


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


@pytest.fixture
def db(request):
    db = request.param()
    yield db
    db.teardown()


DATABASES = [
    createInMemoryDb,
    # createPostgresDb,
]


@pytest.mark.parametrize('db', DATABASES, indirect=True)
class TestDatabase:
    def populate_search_blocks(self, db):
        metadatas = [
            SearchMetadata(
                search_index_type='ExhaustiveSearchIndex',
                starting_search_index=ExhaustiveSearchIndex(n=i),
                ending_search_index=ExhaustiveSearchIndex(n=i+1))
            for i in range(1, 10, 2)]
        db.insert_search_blocks(metadatas)

    def test_initially_empty(self, db):
        assert len(db.load()) == 0
        with pytest.raises(ValueError):
            db.claim_next_search_block(
                search_index_type='ExhaustiveSearchIndex')

    def test_insert_search_block(self, db):
        metadata = SearchMetadata(
            search_index_type='ExhaustiveSearchIndex',
            starting_search_index=ExhaustiveSearchIndex(n=1),
            ending_search_index=ExhaustiveSearchIndex(n=2),
        )
        db.insert_search_blocks([metadata])
        actual = db.claim_next_search_block(
            search_index_type='ExhaustiveSearchIndex')
        assert actual.state == SearchBlockState.IN_PROGRESS
        assert actual.key() == metadata.key()

        # no remaining unstarted blocks
        with pytest.raises(ValueError):
            db.claim_next_search_block(
                search_index_type='ExhaustiveSearchIndex')

    def test_claim_search_block_timestamp_updated(self, db):
        metadata = SearchMetadata(
            search_index_type='ExhaustiveSearchIndex',
            starting_search_index=ExhaustiveSearchIndex(n=1),
            ending_search_index=ExhaustiveSearchIndex(n=2),
        )
        db.insert_search_blocks([metadata])
        actual = db.claim_next_search_block(
            search_index_type='ExhaustiveSearchIndex')
        assert actual.start_time != None

    def test_claim_multiple_blocks(self, db):
        self.populate_search_blocks(db)
        block = db.claim_next_search_block(
            search_index_type='ExhaustiveSearchIndex')
        next_block = db.claim_next_search_block(
            search_index_type='ExhaustiveSearchIndex')
        assert block != next_block

    def test_claim_and_finish_search_block(self, db):
        self.populate_search_blocks(db)
        block = db.claim_next_search_block(
            search_index_type='ExhaustiveSearchIndex')

        records = [
            RiemannDivisorSum(n=1, divisor_sum=1, witness_value=1),
            RiemannDivisorSum(n=2, divisor_sum=2, witness_value=2),
        ]

        db.finish_search_block(block, records)
        assert set(db.load()) == set(records)

        next_block = db.claim_next_search_block(
            search_index_type='ExhaustiveSearchIndex')
        assert block != next_block

    def test_finish_search_block_timestamp_updated(self, db):
        self.populate_search_blocks(db)
        block = db.claim_next_search_block(
            search_index_type='ExhaustiveSearchIndex')

        records = [
            RiemannDivisorSum(n=1, divisor_sum=1, witness_value=1),
            RiemannDivisorSum(n=2, divisor_sum=2, witness_value=2),
        ]

        db.finish_search_block(block, records)
        metadata = [
            x for x in db.load_metadata()
            if x.state == SearchBlockState.FINISHED
        ][0]
        assert metadata.end_time != None

    def test_search_block_with_mpz_values(self, db):
        metadatas = [
            SearchMetadata(
                search_index_type='SuperabundantEnumerationIndex',
                starting_search_index=SuperabundantEnumerationIndex(
                    level=i, index_in_level=0),
                ending_search_index=SuperabundantEnumerationIndex(level=i+1, index_in_level=0))
            for i in range(1, 10, 2)]
        db.insert_search_blocks(metadatas)

        block = db.claim_next_search_block(
            search_index_type='SuperabundantEnumerationIndex')

        records = [
            RiemannDivisorSum(n=mpz(1), divisor_sum=mpz(1), witness_value=1),
            RiemannDivisorSum(n=mpz(2), divisor_sum=mpz(2), witness_value=2),
        ]

        db.finish_search_block(block, records)
        stored = db.load()
        assert len(stored) == 1
        assert stored[0].n == 2

    def test_summarize_empty(self, db):
        expected = SummaryStats(largest_computed_n=None,
                                largest_witness_value=None)

        assert expected == db.summarize()

    def test_summarize_nonempty(self, db):
        self.populate_search_blocks(db)
        block = db.claim_next_search_block(
            search_index_type='ExhaustiveSearchIndex')
        records = [
            RiemannDivisorSum(n=9, divisor_sum=3, witness_value=3),
            RiemannDivisorSum(n=4, divisor_sum=4, witness_value=4),
        ]
        db.finish_search_block(block, records)
        expected = SummaryStats(largest_computed_n=records[0],
                                largest_witness_value=records[1])

        assert expected == db.summarize()
