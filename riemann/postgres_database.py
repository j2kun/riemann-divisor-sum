from typing import List
from typing import Union

import psycopg2.extras
from gmpy2 import mpz
from riemann.database import DivisorDb
from riemann.types import deserialize_search_index
from riemann.types import RiemannDivisorSum
from riemann.types import SearchMetadata
from riemann.types import SummaryStats

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
        CREATE TABLE IF NOT EXISTS RiemannDivisorSums (
            n mpz,
            divisor_sum mpz,
            witness_value double precision
        );''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS SearchMetadata (
            start_time timestamp,
            end_time timestamp,
            search_index_type TEXT,
            starting_search_index TEXT,
            ending_search_index TEXT,
            block_hash CHAR(64)
        );''')
        self.connection.commit()

    def convert_records(self, rows):
        return [
            RiemannDivisorSum(n=mpz(row[0]),
                              divisor_sum=mpz(row[1]),
                              witness_value=row[2]) for row in rows
        ]

    def load(self) -> List[RiemannDivisorSum]:
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT n, divisor_sum, witness_value
            FROM RiemannDivisorSums
            ORDER BY n asc;
        ''')
        return self.convert_records(cursor.fetchall())

    def insert(self, records: List[RiemannDivisorSum]) -> None:
        cursor = self.connection.cursor()
        query = '''
        INSERT INTO
            RiemannDivisorSums(n, divisor_sum, witness_value)
            VALUES %s;
        '''
        template = "(%s::mpz, %s::mpz, %s)"
        arglist = [("%s" % record.n, "%s" % record.divisor_sum,
                    float(record.witness_value)) for record in records]

        psycopg2.extras.execute_values(cur=cursor,
                                       sql=query,
                                       argslist=arglist,
                                       template=template)
        self.connection.commit()

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

    def latest_search_metadata(
            self, search_index_type: str) -> Union[SearchMetadata, None]:
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT
              start_time,
              end_time,
              search_index_type,
              starting_search_index,
              ending_search_index
            FROM SearchMetadata
            WHERE search_index_type = '%s'
            ORDER BY end_time DESC
            LIMIT 1;
        ''' % search_index_type)

        row = cursor.fetchone()
        if not row:
            return None

        return SearchMetadata(
            start_time=row[0],
            end_time=row[1],
            search_index_type=row[2],
            starting_search_index=deserialize_search_index(
                search_index_type, row[3]),
            ending_search_index=deserialize_search_index(
                search_index_type, row[4]),
        )

    def insert_search_metadata(self, metadata: SearchMetadata) -> None:
        cursor = self.connection.cursor()
        query = '''
        INSERT INTO
            SearchMetadata(
              start_time,
              end_time,
              search_index_type,
              starting_search_index,
              ending_search_index,
              block_hash
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        '''

        cursor.execute(
            cursor.mogrify(query, (
                metadata.start_time,
                metadata.end_time,
                metadata.search_index_type,
                metadata.starting_search_index.serialize(),
                metadata.ending_search_index.serialize(),
                metadata.block_hash)))
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
