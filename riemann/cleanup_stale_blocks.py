'''
A job that repeatedly looks for stale search blocks, and marks them as failed.
'''
from datetime import datetime
from datetime import timedelta
from typing import List
import time

from riemann.database import DivisorDb
from riemann.postgres_database import PostgresDivisorDb
from riemann.types import SearchBlockState
from riemann.types import SearchMetadata


def get_stale_blocks(
        all_metadata: List[SearchMetadata],
        staleness_duration: timedelta,
        relative_time: datetime = None) -> List[SearchMetadata]:
    '''Return search blocks that are considered stale.'''
    if not relative_time:
        relative_time = datetime.now()

    return [
        block for block in all_metadata
        if (
            block.state in [SearchBlockState.IN_PROGRESS]
            and relative_time - block.start_time > staleness_duration
        )
    ]


def main(divisorDb: DivisorDb,
         refresh_period_seconds: int = None,
         staleness_duration: timedelta = None) -> None:
    while True:
        try:
            all_metadata = divisorDb.load_metadata()
            stale_blocks = get_stale_blocks(all_metadata, staleness_duration)

            print(f"Marking {len(stale_blocks)} stale blocks as failed")
            for block in stale_blocks:
                divisorDb.mark_block_as_failed(block)
                print(f"Marked block as failed: {block}")

            failure_count = 0
        except ValueError as e:
            print(f"Failed with error: {e}")
            failure_count += 1
            if failure_count > 7:
                print(f"Failed {failure_count} times, quitting.")
                raise e

        time.sleep(refresh_period_seconds)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--data_source_name',
        type=str,
        help='The psycopg data_source_name string'
    )
    parser.add_argument(
        '--refresh_period_seconds',
        type=int,
        default=60*15,
        help='The duration to wait between staleness checks'
    )
    parser.add_argument(
        '--stale_threshold_hours',
        type=int,
        default=2,
        help='The duration after which a search block is considered stale'
    )

    args = parser.parse_args()
    db = PostgresDivisorDb(data_source_name=args.data_source_name)
    main(
        db,
        refresh_period_seconds=args.refresh_period_seconds,
        staleness_duration=timedelta(hours=args.stale_threshold_hours)
    )
