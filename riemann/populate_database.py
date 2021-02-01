'''A simple cli to populate the database.'''
from datetime import datetime

from riemann.database import DivisorDb
from riemann.postgres_database import PostgresDivisorDb
from riemann.search_strategy import search_strategy_by_name
from riemann.search_strategy import SearchStrategy
from riemann.types import SearchMetadata
from riemann.types import hash_divisor_sums

DEFAULT_BATCH_SIZE = 250000
THRESHOLD_WITNESS_VALUE = 1.767


def search_strategy(divisorDb: DivisorDb,
                    search_strategy_name: str) -> SearchStrategy:
    '''Load the approprate search strategy from the database.

    If there is no such strategy, use the default starting state.
    '''
    search_strategy_class = search_strategy_by_name(search_strategy_name)
    print(f"Searching with strategy {search_strategy_name}")
    latest_metadata = divisorDb.latest_search_metadata(
        search_strategy_class().search_state().__class__.__name__)
    if not latest_metadata:
        print("Could not find an existing search state in the DB. "
              "Using default.")
        starting_search_state = search_strategy_class().search_state()
    else:
        starting_search_state = latest_metadata.ending_search_state
    print(f"Starting from search state {starting_search_state}")
    return search_strategy_class().starting_from(starting_search_state)


def populate_db(divisorDb: DivisorDb,
                search_strategy: SearchStrategy, batch_size: int) -> None:
    '''Populate the db in batches.

    Write the computed divisor sums to the database after each batch.
    '''
    while True:
        start = datetime.now()
        start_state = search_strategy.search_state()
        batch_results = search_strategy.next_batch(batch_size)
        end_state = search_strategy.search_state()

        # Only save riemann sums above the threshold. All other values are
        # dropped, and we store the hash of the witness values instead. To
        # verify, one can recompute a block and comparing hashes.
        db.insert([
            x for x in batch_results
            if x.witness_value > THRESHOLD_WITNESS_VALUE
        ])
        block_hash = hash_divisor_sums(batch_results)
        end = datetime.now()
        print(
            f"Computed [{start_state.serialize()}, {end_state.serialize()}] in {end-start}"
            f" with hash {block_hash}"
        )
        divisorDb.insert_search_metadata(
            SearchMetadata(start_time=start,
                           end_time=end,
                           search_state_type=end_state.__class__.__name__,
                           starting_search_state=start_state,
                           ending_search_state=end_state,
                           block_hash=block_hash))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_source_name', type=str,
                        help='The psycopg data_source_name string')
    parser.add_argument('--search_strategy_name', type=str,
                        choices=['ExhaustiveSearchStrategy',
                                 'SuperabundantSearchStrategy'],
                        default='SuperabundantSearchStrategy',
                        help='The search strategy name')
    parser.add_argument('--batch_size', type=int,
                        default=DEFAULT_BATCH_SIZE,
                        help='The size of search batches'
                        )

    args = parser.parse_args()
    db = PostgresDivisorDb(data_source_name=args.data_source_name)
    search_strategy_name = args.search_strategy_name
    batch_size = args.batch_size

    try:
        populate_db(
            db,
            search_strategy(db, search_strategy_name),
            batch_size,
        )
    except KeyboardInterrupt:
        print("Stopping and printing stats...")
    finally:
        best_witness = db.summarize().largest_witness_value
        print(f"Best witness: {best_witness}")
