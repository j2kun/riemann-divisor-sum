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
    parser.add_argument(
        '--fit_log',
        action='store_true',
        default=False,
        help='Whether to fit to a reciprocal or a log, default is reciprocal'
    )
    args = parser.parse_args()
    df = vaex.from_csv(args.divisor_sums_csv_path)

    pts = list(
        zip(df['log_n'].values, df['cumulative_max_witness_value'].values))
    max_pt = pts[-1]
    pts = [(x, y) for (x, y) in pts if y < max_pt[1]]

    x, y = zip(*pts)

    if args.fit_log:
        def func(x, a, b, c):
            return a + b * np.log(x) + c * np.log(np.log(x))
        guess = np.array([1, 1, 1])
    else:
        def func(x, a, b):
            return a + b / x
        guess = np.array([1, 1])

    params, cov = curve_fit(func, x, y, guess)

    if args.fit_log:
        for x in range(300, 10000):
            if func(x, *params) > 1.782:
                print(x)
                break
    else:
        print(params[1])

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
