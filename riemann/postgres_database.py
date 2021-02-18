from typing import List
from typing import Union
from dataclasses import replace

import psycopg2.extras
from gmpy2 import mpz
from riemann.database import DivisorDb
from riemann.types import deserialize_search_index
from riemann.types import RiemannDivisorSum
from riemann.types import SearchBlockState
from riemann.types import SearchMetadata
from riemann.types import SummaryStats
from riemann.types import hash_divisor_sums

DEFAULT_DATA_SOURCE_NAME = 'dbname=divisor'


class PostgresDivisorDb(DivisorDb):
    '''A database implementation using postgres.'''

    def __init__(self, data_source_name=None, data_source_dict=None):
        '''Create a database connection.'''
        if data_source_name is None and data_source_dict is None:
            data_source_name = DEFAULT_DATA_SOURCE_NAME

        if data_source_dict is not None:
            self.connection = psycopg2.connect(**data_source_dict)
        else:
            self.connection = psycopg2.connect(data_source_name)

    def initialize_schema(self):
        cursor = self.connection.cursor()
        cursor.execute('''
        CREATE EXTENSION IF NOT EXISTS pgmp;
        ''')
        cursor.execute('''
        CREATE TYPE SearchBlockState AS ENUM (
          'NOT_STARTED',
          'IN_PROGRESS',
          'FINISHED',
          'FAILED'
        );
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS RiemannDivisorSums (
            n mpz,
            divisor_sum mpz,
            witness_value double precision
        );''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS SearchMetadata (
            creation_time timestamp,
            start_time timestamp,
            end_time timestamp,
            search_index_type TEXT,
            state SearchBlockState,
            starting_search_index TEXT,
            ending_search_index TEXT,
            block_hash CHAR(64),
            UNIQUE (
                search_index_type,
                starting_search_index,
                ending_search_index
            )
        );''')
        self.connection.commit()

    def convert_records(self, rows):
        return [
            RiemannDivisorSum(n=mpz(row[0]),
                              divisor_sum=mpz(row[1]),
                              witness_value=row[2]) for row in rows
        ]

    def convert_metadatas(self, rows):
        return [
            SearchMetadata(
                starting_search_index=deserialize_search_index(row[2], row[0]),
                ending_search_index=deserialize_search_index(row[2], row[1]),
                search_index_type=row[2],
                # indexing [ ] is Python's "name to enum" lookup
                state=SearchBlockState[row[3]],
                creation_time=row[4],
                start_time=row[5],
                end_time=row[6],
                block_hash=row[7],
            ) for row in rows
        ]

    def load(self) -> List[RiemannDivisorSum]:
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT n, divisor_sum, witness_value
            FROM RiemannDivisorSums
            ORDER BY n asc;
        ''')
        return self.convert_records(cursor.fetchall())

    def load_metadata(self) -> List[SearchMetadata]:
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT
              starting_search_index,
              ending_search_index,
              search_index_type,
              state,
              creation_time,
              start_time,
              end_time,
              block_hash
            FROM SearchMetadata
            ORDER BY creation_time asc;
        ''')
        if cursor.rowcount <= 0:
            return []
        return self.convert_metadatas(cursor.fetchall())

    def summarize(self) -> SummaryStats:
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT
                max(n) as largest_computed_n,
                max(witness_value) as largest_witness_value
            FROM RiemannDivisorSums;
        ''')

        max_n, max_witness = cursor.fetchone()
        if max_n is None or max_witness is None:
            return SummaryStats(largest_computed_n=None,
                                largest_witness_value=None)

        cursor.execute('''
            SELECT
                n, divisor_sum, witness_value
            FROM RiemannDivisorSums
            WHERE
                n = '%s'::mpz
                OR witness_value = %s
            ;
        ''' % (max_n, max_witness))

        records = self.convert_records(cursor.fetchall())
        largest_n_record = [r for r in records if r.n == mpz(max_n)][0]
        largest_witness_record = [
            r for r in records if r.witness_value == max_witness
        ][0]

        return SummaryStats(largest_computed_n=largest_n_record,
                            largest_witness_value=largest_witness_record)

    def insert_search_blocks(self, blocks: List[SearchMetadata]) -> None:
        blocks_to_insert = [
            replace(block, state=SearchBlockState.NOT_STARTED)
            for block in blocks
        ]
        cursor = self.connection.cursor()
        query = '''
        INSERT INTO
            SearchMetadata(
              creation_time,
              start_time,
              end_time,
              search_index_type,
              state,
              starting_search_index,
              ending_search_index,
              block_hash
            )
            VALUES %s;
        '''
        template = "(%s, %s, %s, %s, %s, %s, %s, %s)"

        arglist = [
            (
                block.creation_time,
                block.start_time,
                block.end_time,
                block.search_index_type,
                block.state.name,
                block.starting_search_index.serialize(),
                block.ending_search_index.serialize(),
                block.block_hash
            )
            for block in blocks
        ]
        psycopg2.extras.execute_values(cur=cursor,
                                       sql=query,
                                       argslist=arglist,
                                       template=template)
        self.connection.commit()

    def claim_next_search_block(
        self,
        search_index_type: str
    ) -> Union[SearchMetadata, None]:
        cursor = self.connection.cursor()
        # FOR UPDATE locks the row for the duration of the query.
        # Cf. https://stackoverflow.com/q/11532550/438830
        # and test_multiple_processors_no_duplicates
        cursor.execute('''
            UPDATE SearchMetadata
            SET
              start_time = NOW(),
              state = 'IN_PROGRESS'
            FROM (
                SELECT
                    search_index_type,
                    starting_search_index,
                    ending_search_index
                FROM SearchMetadata
                WHERE
                  search_index_type='%s'
                  AND (state = 'NOT_STARTED' OR state = 'FAILED')
                ORDER BY creation_time ASC
                LIMIT 1
                FOR UPDATE
            ) as m
            WHERE
              SearchMetadata.search_index_type = m.search_index_type
              AND SearchMetadata.starting_search_index = m.starting_search_index
              AND SearchMetadata.ending_search_index = m.ending_search_index
            RETURNING
              SearchMetadata.starting_search_index,
              SearchMetadata.ending_search_index,
              SearchMetadata.search_index_type,
              SearchMetadata.start_time,
              SearchMetadata.state
            ;
        ''' % search_index_type)

        if cursor.rowcount <= 0:
            raise ValueError('No legal search block to claim')
        row = cursor.fetchone()
        self.connection.commit()

        return SearchMetadata(
            starting_search_index=deserialize_search_index(
                search_index_type, row[0]),
            ending_search_index=deserialize_search_index(
                search_index_type, row[1]),
            search_index_type=row[2],
            start_time=row[3],
            # indexing [ ] is Python's "name to enum" lookup
            state=SearchBlockState[row[4]],
        )

    def finish_search_block(self,
                            metadata: SearchMetadata,
                            divisor_sums: List[RiemannDivisorSum]) -> None:
        cursor = self.connection.cursor()
        block_hash = hash_divisor_sums(divisor_sums)
        metadata = replace(metadata, block_hash=block_hash)
        query = '''
        UPDATE SearchMetadata
        SET
          end_time = NOW(),
          state = 'FINISHED',
          block_hash = %s
        WHERE
          search_index_type = %s
          AND starting_search_index = %s
          AND ending_search_index = %s
          AND state = 'IN_PROGRESS'
        ;
        '''

        cursor.execute(
            cursor.mogrify(query, (
                metadata.block_hash,
                metadata.search_index_type,
                metadata.starting_search_index.serialize(),
                metadata.ending_search_index.serialize())))

        if cursor.rowcount <= 0:
            self.connection.rollback()
            raise ValueError(
                f"The block was not found or not IN_PROGRESS! "
                f"metadata={metadata}")

        query = '''
        INSERT INTO
            RiemannDivisorSums(n, divisor_sum, witness_value)
            VALUES %s;
        '''
        template = "(%s::mpz, %s::mpz, %s)"
        arglist = [
            ("%s" % d.n, "%s" % d.divisor_sum, float(d.witness_value))
            for d in divisor_sums
            if d.witness_value > self.threshold_witness_value
        ]

        psycopg2.extras.execute_values(cur=cursor,
                                       sql=query,
                                       argslist=arglist,
                                       template=template)
        self.connection.commit()

    def mark_block_as_failed(self, metadata: SearchMetadata) -> None:
        cursor = self.connection.cursor()
        query = '''
        UPDATE SearchMetadata
        SET
          state = 'FAILED'
        WHERE
          search_index_type = %s
          AND starting_search_index = %s
          AND ending_search_index = %s
        ;
        '''

        cursor.execute(
            cursor.mogrify(query, (
                metadata.search_index_type,
                metadata.starting_search_index.serialize(),
                metadata.ending_search_index.serialize())))
        self.connection.commit()


if __name__ == "__main__":
    import sys
    # dsn is a string that specifies the database name
    # and any additional config,
    # e.g., 'dbname=divisor'
    data_source_name = None
    if len(sys.argv) == 2:
        data_source_name = sys.argv[1]

    db = PostgresDivisorDb(data_source_name=data_source_name)
    db.initialize_schema()
    db.connection.close()
