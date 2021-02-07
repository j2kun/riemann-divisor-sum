'''
A job that repeatedly attempts to claim search blocks, computes their divisor
sums, and stores them in the database.
'''
from datetime import datetime
import time

from riemann.database import DivisorDb
from riemann.postgres_database import PostgresDivisorDb
from riemann.search_strategy import search_strategy_by_name
from riemann.search_strategy import SearchStrategy
from riemann.types import SearchMetadata


def claim_and_compute_one_block(
        divisorDb: DivisorDb,
        search_strategy: SearchStrategy) -> None:
    '''Claim and compute a single search block.'''
    try:
        start = datetime.now()
        block = divisorDb.claim_next_search_block(search_strategy.index_name())
        divisor_sums = search_strategy.process_block(block)
        divisorDb.finish_search_block(block, divisor_sums)
        end = datetime.now()
        print(
            f"Computed and saved ["
            f"{block.starting_search_index.serialize()}, "
            f"{block.ending_search_index.serialize()}] "
            f"in {end-start}"
        )
    except ValueError as e:
        print(
            f"Failed to claim or process search block.\n"
            f"Error was: {e}"
        )
        raise e


def main(
        divisorDb: DivisorDb,
        search_strategy: SearchStrategy) -> None:
    '''Repeatedly look for search blocks to process.'''
    failure_count = 0
    while True:
        try:
            claim_and_compute_one_block(divisorDb, search_strategy)
            failure_count = 0
        except ValueError as e:
            failure_count += 1
            if failure_count > 7:
                print(f"Failed {failure_count} times, quitting.")
                return

            sleep_seconds = 1 + 2**failure_count
            print(f"Sleeping and trying again in {sleep_seconds} seconds.")
            time.sleep(sleep_seconds)


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

    args = parser.parse_args()
    db = PostgresDivisorDb(data_source_name=args.data_source_name)
    search_strategy_name = args.search_strategy_name
    search_strategy = search_strategy_by_name(search_strategy_name)()
    main(db, search_strategy)
