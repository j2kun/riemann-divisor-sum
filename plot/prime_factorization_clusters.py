from bokeh.models import HoverTool, ColumnDataSource, LinearColorMapper
from bokeh.palettes import Spectral10
from bokeh.plotting import figure, output_file, save
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import numpy as np
import os.path
import pandas as pd
import umap


def hover_data(df):
    data = []
    cols_to_use = ['num_prime_factors',
                   'num_distinct_prime_factors', '2', '3', '5', '7', '11', '13']

    for index, row in df.iterrows():
        data.append(','.join(["{:.3f}".format(row[col])
                              for col in cols_to_use]))

    return data


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--divisor_sums_csv_path',
        type=str,
        help='The csv file containing divisor sum data'
    )
    parser.add_argument(
        '--embedding_path',
        type=str,
        default='embedding.npy',
        help='The file containing a precomputed embedding'
    )
    args = parser.parse_args()
    df = pd.read_csv(args.divisor_sums_csv_path)
    df = df.loc[df['witness_value'] >= 1.69]
    df[['witness_value']] = StandardScaler().fit_transform(df[['witness_value']])

    # extra features, and normalizing each prime factor column
    prime_cols = cols = list(df)[2:]
    df['num_prime_factors'] = df[prime_cols].sum(axis=1)
    df['num_distinct_prime_factors'] = df[prime_cols].astype(bool).sum(axis=1)
    for col in prime_cols:
        df[col] = df[col] / df['num_prime_factors']

    # to normalize all columns, use this instead of the previous line
    # df[df.columns.values.tolist()] = StandardScaler().fit_transform(df[df.columns.values.tolist()])
    print(df.describe())

    if os.path.isfile(args.embedding_path):
        print("Loading pre-existing embedding")
        embedding = np.load(args.embedding_path)
    else:
        df = df.drop('log_n', axis=1)
        df = df.loc[:, (df != 0).any(axis=0)]
        reducer = umap.UMAP()
        embedding = reducer.fit_transform(df.values)
        print(embedding.shape)
        print(f"Saving to {args.embedding_path}")
        np.save(args.embedding_path, embedding)

    embedding_df = pd.DataFrame(embedding, columns=('x', 'y'))
    embedding_df['witness_value'] = df['witness_value']
    print("starting historgramming")
    embedding_df['hover'] = hover_data(df)

    output_file(filename="umap_viz.html",
                title="UMAP visualization of witness values")
    plot_figure = figure(
        title='UMAP projection of the witness value dataset',
        plot_width=600,
        plot_height=600,
        tools=('pan, wheel_zoom, reset')
    )
    color_mapping = LinearColorMapper(
        palette=Spectral10,
        low=embedding_df['witness_value'].min(),
        high=embedding_df['witness_value'].max()
    )
    datasource = ColumnDataSource(embedding_df)

    plot_figure.add_tools(HoverTool(tooltips="""
    <div>
        <div>
            @hover
        </div>
        <div>
            <span style='font-size: 16px; color: #224499'>Witness value:</span>
            <span style='font-size: 18px'>@witness_value</span>
        </div>
    </div>
    """))

    plot_figure.circle(
        'x',
        'y',
        source=datasource,
        color=dict(field='witness_value', transform=color_mapping),
        line_alpha=0.6,
        fill_alpha=0.6,
        size=4
    )

    save(plot_figure)
