from math import ceil

from matplotlib import pyplot as plt
import pandas as pd

PACKAGES_ROOT = "/mnt/fs00/rabl/ilin.tolovski/stork-01-03-2021/packages/"


def addlabels(x, y):
    for i in range(0, len(x)):
        # print(y.iloc[i])
        plt.text(x=i, y=y.iloc[i], s=y.iloc[i], ha="center")


def topX(df, X, output_file):
    df.sort_values(by="count", ascending=False, inplace=True)
    if X < len(df):
        subset = df.iloc[:X][:]
    else:
        subset = df
    print(subset)
    plt.figure(figsize=(12, 9))
    plt.bar(x=subset["library"], height=subset["count"], width=0.7,
            label="Usage of Python Packages across Repositories")
    addlabels(x=subset["library"], y=subset["count"])
    plt.xlabel("Python Packages")
    plt.ylabel("# of Occurences")
    plt.ylim(0, max(subset["count"]) + 10)
    plt.xticks(rotation=60)
    plt.yticks(range(0, (max(subset["count"]) + max(subset["count"]) // 10),
                     (max(subset["count"]) + max(subset["count"]) // 10) // 5))
    plt.tight_layout()
    # plt.show()
    plt.savefig(fname=output_file, dpi=600, pad_inches=0.2)


def data_processing_libs(df, output_file):
    libraries = ['pandas', 'cudf', 'pyspark', 'spark', 'dask', 'arrow', 'duckdb', 'modin', 'polars', 'dplyr',
                 'clickhouse_connect', 'datatable']
    lib_df = pd.DataFrame(columns=["library", "count"])
    for library in libraries:
        p = df[df["library"] == library]
        if p.empty:
            print(f"p is empty {p['library']}")
            lib_df = lib_df.append(pd.DataFrame(data={'library': library, 'count': 0}, index=[0]), ignore_index=True)

        else:
            lib_df = lib_df.append(p, ignore_index=True)
    lib_df.sort_values(by="count", ascending=False, inplace=True)
    print(lib_df)

    topX(df=lib_df, X=len(lib_df), output_file=output_file)


occurences_df = pd.read_csv(filepath_or_buffer=f"{PACKAGES_ROOT}occurences.csv", header=0)

topX(df=occurences_df, X=15, output_file=f"{PACKAGES_ROOT}summary.pdf")
data_processing_libs(df=occurences_df, output_file=f"{PACKAGES_ROOT}data_libraries.pdf")
