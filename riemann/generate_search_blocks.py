'''
A job that repeatedly checks to see if the database is running low on eligible
search blocks to claim, and computes and inserts new search blocks if it is.
'''
from datetime import datetime
from typing import List
import time

from riemann.database import DivisorDb
from riemann.postgres_database import PostgresDivisorDb
from riemann.search_strategy import SearchStrategy
from riemann.search_strategy import search_strategy_by_name
from riemann.types import SearchBlockState
from riemann.types import SearchIndex
from riemann.types import SearchMetadata
from riemann.types import index_name_to_class


def get_eligible_blocks(
        all_metadata: List[SearchMetadata]) -> List[SearchMetadata]:
    '''Return search blocks that are eligible to be claimed.'''
    return [
        block for block in all_metadata
        if block.state in [SearchBlockState.NOT_STARTED, SearchBlockState.FAILED]
    ]


def get_starting_index(
        search_strategy: SearchStrategy,
        all_metadata: List[SearchMetadata],
        eligible_blocksl: List[SearchMetadata]) -> SearchIndex:
    '''Return the starting index to use for the next set of search blocks.'''
    if len(all_metadata) == 0:
        return index_name_to_class(search_strategy.index_name())()
    else:
        indices = [b.ending_search_index for b in all_metadata]
        last_index = search_strategy.max(indices)
        # this is a bit of a hack. The search ranges are inclusive, so the
        # last_index already has a divisor sum in the database.  we need to go
        # one step further, but the interface doesn't quite support it yet. So
        # we generate one more block of size one.
        return search_strategy.starting_from(last_index).generate_search_blocks(
            count=1, batch_size=1
        )[0].ending_search_index


def main(divisorDb: DivisorDb,
         search_strategy: SearchStrategy,
         args=None) -> None:
    failure_count = 0
    while True:
        try:
            start = datetime.now()
            all_metadata = divisorDb.load_metadata()
            eligible_blocks = get_eligible_blocks(all_metadata)

            if len(eligible_blocks) < args.refresh_threshold:
                starting_index = get_starting_index(
                    search_strategy,
                    all_metadata,
                    eligible_blocks)
                new_blocks = search_strategy.starting_from(
                    starting_index).generate_search_blocks(
                    count=args.refresh_count,
                    batch_size=args.block_size
                )
                divisorDb.insert_search_blocks(new_blocks)
                end = datetime.now()
                print(
                    f"Computed {len(new_blocks)} new search blocks "
                    f"in {end-start}"
                )
            else:
                print(
                    f"Found {len(eligible_blocks)} eligible blocks. "
                    f"Waiting until less than {args.refresh_threshold} to refresh."
                )

            failure_count = 0
        except ValueError as e:
            print(f"Failed with error: {e}")
            failure_count += 1
            if failure_count > 7:
                print(f"Failed {failure_count} times, quitting.")
                return

        time.sleep(args.refresh_period_seconds)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--data_source_name',
        type=str,
        help='The psycopg data_source_name string'
    )
    parser.add_argument(
        '--search_strategy_name',
        type=str,
        choices=['ExhaustiveSearchStrategy', 'SuperabundantSearchStrategy'],
        default='SuperabundantSearchStrategy',
        help='The search strategy name'
    )
    parser.add_argument(
        '--block_size',
        type=int,
        default=250000,
        help='The size of a single search block'
    )
    parser.add_argument(
        '--refresh_count',
        type=int,
        default=100,
        help='The number of blocks to generate at a time'
    )
    parser.add_argument(
        '--refresh_threshold',
        type=int,
        default=100,
        help='The minimum number of blocks before generating a new batch'
    )
    parser.add_argument(
        '--refresh_period_seconds',
        type=int,
        default=30,
        help='The number of seconds to wait between refresh checks'
    )

    args = parser.parse_args()
    db = PostgresDivisorDb(data_source_name=args.data_source_name)
    search_strategy_name = args.search_strategy_name
    search_strategy = search_strategy_by_name(search_strategy_name)()
    main(db, search_strategy, args)
