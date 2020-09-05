'''A simple cli to populate the database.'''
import time
from riemann.database import DivisorDb
from riemann.divisor import compute_riemann_divisor_sums
from riemann.in_memory_database import InMemoryDivisorDb


def populate_db(db: DivisorDb, batch_size: int = 100000) -> None:
    '''Populate the db in batches.

    Write the computed divisor sums to the database after each batch.
    '''
    starting_n = (db.summarize().largest_computed_n.n or 5040) + 1
    while True:
        ending_n = starting_n + batch_size
        start = time.time()
        db.upsert(compute_riemann_divisor_sums(starting_n, ending_n))
        end = time.time()
        print(f"Computed [{starting_n}, {ending_n}] in {end-start} seconds")
        starting_n = ending_n + 1


if __name__ == "__main__":
    db = InMemoryDivisorDb()
    try:
        populate_db(db)
    except KeyboardInterrupt:
        print("Stopping and printing stats...")
    finally:
        best_witness = db.summarize().largest_witness_value
        print(f"Best witness: {best_witness}")
