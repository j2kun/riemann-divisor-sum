import pandas as pd
import numpy as np


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--divisor_sums_csv_path',
        type=str,
        help='The csv file containing divisor sum data'
    )
    args = parser.parse_args()

    chunksize = 20000000
    the_max = 0
    i = 0
    with pd.read_csv(args.divisor_sums_csv_path, chunksize=chunksize) as reader:
        for chunk in reader:
            print(f"chunk {i}")
            if i == 0:
                chunk = chunk[chunk['log_n'] > 9.35]
            maxes = np.maximum.accumulate(chunk.witness_value)
            maxes = np.maximum(maxes, the_max)
            the_max = np.max(maxes)
            chunk['cumulative_max_witness_value'] = maxes
            chunk.to_csv(
                f"divisor_sums_with_max.csv",
                header=(i == 0),
                columns=['log_n', 'witness_value', 'cumulative_max_witness_value'],
                mode='a')
            i += 1
