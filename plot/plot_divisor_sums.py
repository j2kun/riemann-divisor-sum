import vaex
import numpy
import matplotlib.pyplot as plt


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--divisor_sums_csv_path',
        type=str,
        help='The csv file containing divisor sum data'
    )
    parser.add_argument(
        '--divisor_sums_hdf5_path',
        type=str,
        help='The hdf5 file containing divisor sum data'
    )
    args = parser.parse_args()

    if args.divisor_sums_csv_path:
        df = vaex.from_csv(args.divisor_sums_csv_path)
    else:
        # can convert to an hdf5 once using
        # vaex.from_csv('divisor_sums.csv', convert=True, chunk_size=5_000_000) 
        df = vaex.open(args.divisor_sums_hdf5_path)

    df.select(df.log_n > 12.3, name='log_n_min')
    df.select(df.witness_value > 1.68, name='witness_value_min')

    df.viz.heatmap(
        df.log_n, 
        df.witness_value, 
        limits=['minmax', [1.68, 1.782]],
        selection=['witness_value_min', 'log_n_min'],
        colormap='coolwarm', 
        ylabel='witness_value',
        xlabel='$\log(n)$',
        show=True
    )
    plt.clf()

    df.viz.scatter(
        df.log_n, 
        df.cumulative_max_witness_value, 
        ylabel='witness_value',
        xlabel='$\log(n)$',
        c="red", 
        alpha=0.5, 
        s=4,
    )
    plt.show()
