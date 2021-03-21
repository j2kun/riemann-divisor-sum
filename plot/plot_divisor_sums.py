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
    args = parser.parse_args()

    df = vaex.from_csv(args.divisor_sums_csv_path)
    df['cumulative_max_witness_value'] = numpy.maximum.accumulate(df.witness_value.values)

    # heatmap
    df.viz.heatmap('log_n', 'witness_value', colormap='coolwarm', show=True)
    plt.clf()

    # scatterplot
    x = df.evaluate("log_n")
    y = df.evaluate("cumulative_max_witness_value")
    plt.scatter(x, y, c="red", alpha=0.5, s=4)
    plt.show()
