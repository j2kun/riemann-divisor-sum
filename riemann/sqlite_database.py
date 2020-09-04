from dataclasses import asdict
from riemann.database import DivisorDb
from riemann.database import RiemannDivisorSum
from riemann.database import SummaryStats
from typing import List
import sqlite3


class SqliteDivisorDb(DivisorDb):
    def __init__(self, database_path=None):
        '''Create a database connection.'''
        if database_path is None:
            raise ValueError("Must specify a database path!")
        self.connection = sqlite3.connect(database_path)

    def initialize_schema(self):
        cursor = self.connection.cursor()
        cursor.execute('''
        CREATE TABLE RiemannDivisorSums (
            n UNSIGNED BIG INT CONSTRAINT divisor_sum_pk PRIMARY KEY,
            divisor_sum UNSIGNED BIG INT,
            witness_value REAL
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


if __name__ == "__main__":
    import sys
    db = SqliteDivisorDb(database_path=sys.argv[1])
    db.initialize_schema()
    db.connection.close()
