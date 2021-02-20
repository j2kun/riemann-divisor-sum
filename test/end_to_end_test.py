from dataclasses import dataclass
from datetime import timedelta
from multiprocessing import Pool
from multiprocessing import Process
from pytest_cov.embed import cleanup_on_sigterm
from typing import List
import pytest
import testing.postgresql
import time

from riemann import cleanup_stale_blocks
from riemann import generate_search_blocks
from riemann import process_search_blocks
from riemann.database import DivisorDb
from riemann.postgres_database import PostgresDivisorDb
from riemann.search_strategy import SearchStrategy
from riemann.search_strategy import SuperabundantSearchStrategy
from riemann.types import RiemannDivisorSum
from riemann.types import SearchBlockState
from riemann.types import SearchIndex
from riemann.types import SearchMetadata
from riemann.types import SuperabundantEnumerationIndex


cleanup_on_sigterm()


@pytest.fixture
def db_factory():
    tmp_postgres = testing.postgresql.Postgresql()
    database = PostgresDivisorDb(data_source_dict=tmp_postgres.dsn())
    database.initialize_schema()
    # each worker process gets its own database connection
    yield lambda: PostgresDivisorDb(data_source_dict=tmp_postgres.dsn())
    tmp_postgres.stop


@dataclass
class FakeArgs:
    refresh_count: int = 5
    refresh_threshold: int = 3
    block_size: int = 1000
    refresh_period_seconds: int = 3


def make_processor_test_strategy(process_block_fn):
    class TestStrategy(SearchStrategy):
        def index_name(self) -> str:
            return SuperabundantSearchStrategy().index_name()

        def starting_from(self, search_index: SearchIndex) -> SearchStrategy:
            return self

        def generate_search_blocks(self, count: int, batch_size: int) -> List[SearchMetadata]:
            raise Exception('Failing for a test!')

        def process_block(self, block: SearchMetadata) -> List[RiemannDivisorSum]:
            process_block_fn()
            raise Exception('Failing for a test!')

        def max(self, blocks: List[SearchIndex]) -> SearchIndex:
            raise Exception('Failing for a test!')

    return TestStrategy()


def test_generate_and_process_blocks_no_duplicates(db_factory):
    db = db_factory()
    # this ensures nobody removes this attribute without updating this test
    assert db.threshold_witness_value is not None

    # I need to store all witness values in the datbase in order to properly
    # check the possibility of duplicates, because if the duplicates occur,
    # they are likely to occur on a boundary of two search indexes. But if they
    # aren't stored in the DB because one or both has small witness values,
    # this test will not fail. We could instead make the search block size such
    # that a known good value (e.g., 5040) falls on a block boundary, but this
    # is much easier to set up.
    db.threshold_witness_value = 0

    def run_generator():
        generate_search_blocks.main(
            db_factory(),
            search_strategy=SuperabundantSearchStrategy(),
            args=FakeArgs()
        )

    def run_processor():
        process_search_blocks.main(
            db_factory(), search_strategy=SuperabundantSearchStrategy())

    p1 = Process(target=run_generator)
    p1.start()
    p2 = Process(target=run_processor)
    p2.start()
    time.sleep(30)
    p1.terminate()
    p2.terminate()
    time.sleep(5)
    p1.close()
    p2.close()

    metadatas = db.load_metadata()
    assert len(metadatas) > 0

    divisor_sums = db.load()
    assert len(divisor_sums) > 0

    n_values = [d.n for d in divisor_sums]
    assert len(n_values) == len(set(n_values))

    for metadata in metadatas:
        assert (metadata.state != SearchBlockState.FINISHED
                or metadata.block_hash is not None)


def test_multiple_processors_no_duplicates(db_factory):
    db = db_factory()
    # this ensures nobody removes this attribute without updating this test
    assert db.threshold_witness_value is not None
    db.threshold_witness_value = 0

    def run_generator():
        generate_search_blocks.main(
            db_factory(),
            search_strategy=SuperabundantSearchStrategy(),
            # this ensures there are many blocks that are quick
            # to process, maximizing the likelihood of a
            # conflict. For example, this test will fail if the
            # 'FOR UPDATE' is removed from the subquery in
            # claim_next_search_block
            args=FakeArgs(refresh_count=10000, block_size=2)
        )

    def run_processor():
        process_search_blocks.main(
            db_factory(), search_strategy=SuperabundantSearchStrategy())

    p1 = Process(target=run_generator)
    p1.start()
    time.sleep(15)

    worker_count = 5
    workers = []
    for i in range(worker_count):
        workers.append(Process(target=run_processor))
    for worker in workers:
        worker.start()

    time.sleep(30)
    p1.terminate()
    for worker in workers:
        worker.terminate()

    time.sleep(5)
    p1.close()
    for worker in workers:
        worker.close()

    divisor_sums = db.load()
    assert len(divisor_sums) > 0

    n_values = [d.n for d in divisor_sums]
    assert len(n_values) == len(set(n_values))


def test_mark_blocks_failed_when_block_computation_errs(db_factory):
    db = db_factory()

    def run_generator():
        generate_search_blocks.main(
            db_factory(),
            search_strategy=SuperabundantSearchStrategy(),
            args=FakeArgs()
        )

    def raise_fn():
        raise Exception('Failing for a test!')

    def run_processor():
        process_search_blocks.main(
            db_factory(),
            search_strategy=make_processor_test_strategy(raise_fn)
        )

    p1 = Process(target=run_generator)
    p1.start()
    time.sleep(5)
    p2 = Process(target=run_processor)
    p2.start()
    time.sleep(5)
    p1.terminate()
    p2.terminate()
    time.sleep(5)
    p1.close()
    p2.close()

    metadatas = db.load_metadata()
    failed_blocks = [x for x in metadatas if x.state ==
                     SearchBlockState.FAILED]
    assert len(failed_blocks) > 0


def test_mark_stale_blocks_failed(db_factory):
    db = db_factory()

    def run_generator():
        generate_search_blocks.main(
            db_factory(),
            search_strategy=SuperabundantSearchStrategy(),
            args=FakeArgs()
        )

    def slow_process_fn():
        time.sleep(100)

    def run_processor():
        process_search_blocks.main(
            db_factory(),
            search_strategy=make_processor_test_strategy(slow_process_fn)
        )

    def run_cleanup():
        cleanup_stale_blocks.main(
            db_factory(),
            refresh_period_seconds=1,
            staleness_duration=timedelta(seconds=2)
        )

    p1 = Process(target=run_generator)
    p1.start()
    p2 = Process(target=run_cleanup)
    p2.start()
    time.sleep(5)
    p3 = Process(target=run_processor)
    p3.start()
    time.sleep(5)
    p1.terminate()
    p2.terminate()
    p3.terminate()
    time.sleep(5)
    p1.close()
    p2.close()
    p3.close()

    metadatas = db.load_metadata()
    failed_blocks = [x for x in metadatas if x.state ==
                     SearchBlockState.FAILED]
    assert len(failed_blocks) == 1
