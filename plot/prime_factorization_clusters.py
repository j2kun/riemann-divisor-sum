from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import numpy as np
import os.path
import pandas as pd
import umap


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
    df = df.loc[df['witness_value'] >= 1.77]
    df[['witness_value']] = StandardScaler().fit_transform(df[['witness_value']])
    print(df.describe())

    if os.path.isfile(args.embedding_path):
        print("Loading pre-existing embedding")
        embedding = np.load(args.embedding_path)
    else:
        df = df.drop('log_n', axis=1)
        df = df.loc[:, (df != 0).any(axis=0)]
        # normalized_data = StandardScaler().fit_transform(df)
        reducer = umap.UMAP()
        embedding = reducer.fit_transform(df.values)
        print(embedding.shape)
        print(f"Saving to {args.embedding_path}")
        np.save(args.embedding_path, embedding)

    sc = plt.scatter(
        embedding[:, 0],
        embedding[:, 1],
        c=df['witness_value'].values,
        cmap='RdYlBu',
        s=1)
    plt.gca().set_aspect('equal', 'datalim')
    plt.colorbar(sc)
    plt.title('UMAP projection of factorization of RH counterexample candidates', fontsize=12)

    plt.show()
