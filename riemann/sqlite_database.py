from dataclasses import asdict
from riemann.database import DivisorDb
from riemann.database import SearchMetadataDb
from riemann.types import RiemannDivisorSum
from riemann.types import SearchMetadata
from riemann.types import SummaryStats
from riemann.types import deserialize_search_state
from typing import List
from typing import Union
import sqlite3


class SqliteDivisorDb(DivisorDb, SearchMetadataDb):
    def __init__(self, database_path=None):
        '''Create a database connection.'''
        if database_path is None:
            raise ValueError("Must specify a database path!")
        '''
        PARSE_DECLTYPES results in the automated conversion of sqlite
        timestamp to python datetime.
        '''
        self.connection = sqlite3.connect(database_path,
                                          detect_types=sqlite3.PARSE_DECLTYPES)

    def initialize_schema(self):
        cursor = self.connection.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS RiemannDivisorSums (
            n UNSIGNED BIG INT CONSTRAINT divisor_sum_pk PRIMARY KEY,
            divisor_sum UNSIGNED BIG INT,
            witness_value REAL
        );''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS SearchMetadata (
            start_time timestamp,
            end_time timestamp,
            search_state_type TEXT,
            starting_search_state TEXT,
            ending_search_state TEXT
        );''')
        self.connection.commit()

    def convert_records(self, rows):
        return [
            RiemannDivisorSum(n=row[0],
                              divisor_sum=row[1],
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

    def upsert(self, records: List[RiemannDivisorSum]) -> None:
        cursor = self.connection.cursor()
        query = '''
        INSERT INTO
            RiemannDivisorSums(n, divisor_sum, witness_value)
            VALUES(:n, :divisor_sum, :witness_value)
        ON CONFLICT(n) DO UPDATE SET
            divisor_sum=excluded.divisor_sum,
            witness_value=excluded.witness_value;
        '''

        cursor.executemany(query, [asdict(record) for record in records])
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

        cursor.execute(
            '''
            SELECT
                n, divisor_sum, witness_value
            FROM RiemannDivisorSums
            WHERE
                n = :max_n
                OR witness_value = :max_witness;
        ''', {
                'max_n': max_n,
                'max_witness': max_witness
            })

        records = self.convert_records(cursor.fetchall())
        largest_n_record = [r for r in records if r.n == max_n][0]
        largest_witness_record = [
            r for r in records if r.witness_value == max_witness
        ][0]

        return SummaryStats(largest_computed_n=largest_n_record,
                            largest_witness_value=largest_witness_record)

    def latest_search_metadata(
            self, search_state_type: str) -> Union[SearchMetadata, None]:
        cursor = self.connection.cursor()
        cursor.execute(
            '''
            SELECT
              start_time,
              end_time,
              search_state_type,
              starting_search_state,
              ending_search_state
            FROM SearchMetadata
            WHERE search_state_type = :search_state_type
            ORDER BY end_time DESC
            LIMIT 1;
        ''', {'search_state_type': search_state_type})

        row = cursor.fetchone()
        if not row:
            return None

        return SearchMetadata(
            start_time=row[0],
            end_time=row[1],
            search_state_type=row[2],
            starting_search_state=deserialize_search_state(
                search_state_type, row[3]),
            ending_search_state=deserialize_search_state(
                search_state_type, row[4]),
        )

    def insert_search_metadata(self, metadata: SearchMetadata) -> None:
        cursor = self.connection.cursor()
        query = '''
        INSERT INTO
            SearchMetadata(
              start_time,
              end_time,
              search_state_type,
              starting_search_state,
              ending_search_state
            )
            VALUES(
                :start_time,

                :end_time,
                :search_state_type,
                :starting_search_state,
                :ending_search_state)
        '''

        cursor.execute(
            query, {
                'start_time': metadata.start_time,
                'end_time': metadata.end_time,
                'search_state_type': metadata.search_state_type,
                'starting_search_state':
                metadata.starting_search_state.serialize(),
                'ending_search_state':
                metadata.ending_search_state.serialize(),
            })
        self.connection.commit()


if __name__ == "__main__":
    import sys
    db = SqliteDivisorDb(database_path=sys.argv[1])
    db.initialize_schema()
    db.connection.close()
