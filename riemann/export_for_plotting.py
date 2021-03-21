'''
A one-off script that exports the Riemann divisor sums table to a file format
suitable for plotting.
'''

from gmpy2 import log
from riemann.database import DivisorDb
from riemann.postgres_database import PostgresDivisorDb
from typing import TextIO


def main(divisorDb: DivisorDb, output_file: TextIO) -> None:
    output_file.write('log_n,log_divisor_sum,witness_value\n')
    for rds in divisorDb.load():
        log_n = log(rds.n)
        log_divisor_sum = log(rds.divisor_sum)
        output_file.write(
            f'{log_n:.10f},{log_divisor_sum:.10f},{rds.witness_value:.10f}\n')


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--data_source_name',
        type=str,
        help='The psycopg data_source_name string'
    )
    parser.add_argument(
        '--output_file_path',
        type=str,
        default='divisor_sums.csv',
        help='The filepath to write data to (default divisor_sums.csv)'
    )

    args = parser.parse_args()
    db = PostgresDivisorDb(data_source_name=args.data_source_name)
    with open('divisor_sums.csv', 'w') as outfile:
        main(db, outfile)
