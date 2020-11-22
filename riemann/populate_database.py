'''A simple cli to populate the database.'''
from datetime import datetime

from riemann.database import DivisorDb
from riemann.database import SearchMetadataDb
from riemann.postgres_database import PostgresDivisorDb
from riemann.search_strategy import search_strategy_by_name
from riemann.search_strategy import SearchStrategy
from riemann.types import SearchMetadata

DEFAULT_BATCH_SIZE = 250000


def search_strategy(metadataDb: SearchMetadataDb,
                    search_strategy_name: str) -> SearchStrategy:
    '''Load the approprate search strategy from the database.

    If there is no such strategy, use the default starting state.
    '''
    search_strategy_class = search_strategy_by_name(search_strategy_name)
    print(f"Searching with strategy {search_strategy_name}")
    latest_metadata = metadataDb.latest_search_metadata(
        search_strategy_class().search_state().__class__.__name__)
    if not latest_metadata:
        print("Could not find an existing search state in the DB. "
              "Using default.")
        starting_search_state = search_strategy_class().search_state()
    else:
        starting_search_state = latest_metadata.ending_search_state
    print(f"Starting from search state {starting_search_state}")
    return search_strategy_class().starting_from(starting_search_state)


def populate_db(divisorDb: DivisorDb, metadataDb: SearchMetadataDb,
                search_strategy: SearchStrategy, batch_size: int) -> None:
    '''Populate the db in batches.

    Write the computed divisor sums to the database after each batch.
    '''
    while True:
        start = datetime.now()
        start_state = search_strategy.search_state()
        db.upsert(search_strategy.next_batch(batch_size))
        end_state = search_strategy.search_state()
        end = datetime.now()
        print(
            f"Computed [{start_state.serialize()}, {end_state.serialize()}] in {end-start}"
        )
        metadataDb.insert_search_metadata(
            SearchMetadata(start_time=start,
                           end_time=end,
                           search_state_type=end_state.__class__.__name__,
                           starting_search_state=start_state,
                           ending_search_state=end_state))


if __name__ == "__main__":
    import sys
    if len(sys.argv) not in [3, 4]:
        print('''
Usage: python -m riemann.populate_database DATA_SOURCE_NAME SEARCH_STRATEGY_NAME [BATCH_SIZE]

SEARCH_STRATEGY_NAME can be one of

 - ExhaustiveSearchStrategy
 - SuperabundantSearchStrategy
''')

    db = PostgresDivisorDb(data_source_name=sys.argv[1])
    search_strategy_name = sys.argv[2]
    batch_size = int(sys.argv[3]) if len(sys.argv) == 4 else DEFAULT_BATCH_SIZE

    try:
        populate_db(db, db, search_strategy(db, search_strategy_name),
                    batch_size)
    except KeyboardInterrupt:
        print("Stopping and printing stats...")
    finally:
        best_witness = db.summarize().largest_witness_value
        print(f"Best witness: {best_witness}")
