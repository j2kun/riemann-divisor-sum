'''A simple cli to populate the database.'''
from riemann.database import DivisorDb
from riemann.divisor import compute_riemann_divisor_sums
from riemann.search_strategy import ExhaustiveSearchStrategy
from riemann.sqlite_database import SqliteDivisorDb
import time


def populate_db(db: DivisorDb, batch_size: int = 250000) -> None:
    '''Populate the db in batches.

    Write the computed divisor sums to the database after each batch.
    '''
    starting_n = (db.summarize().largest_computed_n.n or 5040) + 1
    search_strategy = ExhaustiveSearchStrategy().starting_from(starting_n)

    while True:
        start = time.time()
        db.upsert(search_strategy.next_batch(batch_size))
        end = time.time()
        print(f"Computed [{starting_n}, {ending_n}] in {end-start} seconds")


if __name__ == "__main__":
    import sys
    db = SqliteDivisorDb(database_path=sys.argv[1])
    try:
        populate_db(db)
    except KeyboardInterrupt:
        print("Stopping and printing stats...")
    finally:
        best_witness = db.summarize().largest_witness_value
        print(f"Best witness: {best_witness}")
