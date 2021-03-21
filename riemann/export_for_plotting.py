'''
A one-off script that exports the Riemann divisor sums table to a file format
suitable for plotting.
'''

from gmpy2 import log
from riemann.database import DivisorDb
from riemann.postgres_database import PostgresDivisorDb
from riemann.primes import primes
from riemann.superabundant import factorize
from typing import TextIO


def export_divisor_sums(divisorDb: DivisorDb, output_file: TextIO) -> None:
    # for now, use only 115 primes for columns
    prime_subset = list(primes[:115])
    prime_columns = ','.join(['%d' % p for p in prime_subset])
    output_file.write('log_n,witness_value,' + prime_columns + '\n')
    for rds in divisorDb.load():
        log_n = log(rds.n)
        factorization = factorize(rds.n, prime_subset)
        factor_columns = ','.join(['%d' % d for (p, d) in factorization])
        output_file.write(
            f'{log_n:.10f},{rds.witness_value:.10f},{factor_columns}\n')


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--data_source_name',
        type=str,
        help='The psycopg data_source_name string'
    )
    parser.add_argument(
        '--divisor_sums_filepath',
        type=str,
        default='divisor_sums.csv',
        help='The filepath to write divisor sum witness values to (default divisor_sums.csv)'
    )

    args = parser.parse_args()
    db = PostgresDivisorDb(data_source_name=args.data_source_name)
    with open(args.divisor_sums_filepath, 'w') as outfile:
        export_divisor_sums(db, outfile)
