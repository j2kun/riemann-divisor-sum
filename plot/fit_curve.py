import vaex
import numpy as np
from scipy.optimize import curve_fit
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

    pts = list(zip(df['log_n'].values, df['cumulative_max_witness_value'].values))
    max_pt = pts[-1]
    pts = [(x, y) for (x,y) in pts if y < max_pt[1]]

    x, y = zip(*pts)
    params = np.array([1, 1])

    def func(x, a, b):
        return a + b / x

    params, cov = curve_fit(func, x, y, params)
    print(params)
    print(cov)

    df['regression_line'] = df.apply(
            lambda x: func(x, *params), [df.log_n])

    df.viz.scatter(
        df.log_n,
        df.cumulative_max_witness_value,
        ylabel='witness_value',
        xlabel='$\log(n)$',
        c="red",
        alpha=0.5,
        s=4,
    )
    plt.plot(
        df.log_n.values,
        df.regression_line.values,
    )

    plt.show()
