import argparse
from math import ceil

from matplotlib import pyplot as plt
import pandas as pd


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
    if max(subset["count"]) == 0:
        return 0
    else:
        print(subset)
        plt.figure(figsize=(12, 9))
        plt.bar(x=subset["library"], height=subset["count"], width=0.7,
                label="Usage of Python Packages across Repositories")
        addlabels(x=subset["library"], y=subset["count"])
        plt.xlabel("Python Packages")
        plt.ylabel("# of Occurences")
        plt.ylim(0, max(subset["count"]) + 10)
        plt.xticks(rotation=60)

        plt.yticks(range(0, (max(subset["count"]) + (max(subset["count"]) // 10)),
                         ((max(subset["count"]) + max(subset["count"]) // 10) // 5) + 1))
        plt.tight_layout()
        # plt.show()
        plt.savefig(fname=output_file, dpi=600, pad_inches=0.2)


def plot_libs(df, libraries, output_file):
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


def data_analysis_libs(occurrences_df):
    libraries = ['pandas', 'cudf', 'pyspark', 'spark', 'dask', 'arrow', 'duckdb', 'modin', 'polars', 'dplyr',
                 'clickhouse_connect', 'datatable']
    plot_libs(df=occurrences_df, libraries=libraries, output_file=f"{args.path}{data_analysis_libs.__name__}.pdf")


def machine_learning_libs(occurrences_df):
    libraries = ['scikit-learn', "torch", "torchvision", "torchaudio", "tensorflow", "tensorboard", "keras", 'theano']
    plot_libs(df=occurrences_df, libraries=libraries, output_file=f"{args.path}{machine_learning_libs.__name__}.pdf")


def visualization_libs(occurrences_df):
    libraries = ["matplotlib", "seaborn", "plotly", "ggplot", "bokeh"]
    plot_libs(df=occurrences_df, libraries=libraries, output_file=f"{args.path}{visualization_libs.__name__}.pdf")


def web_framework_libs(occurrences_df):
    libraries = ["Django", "Flask", "CherryPy", "Bottle", "Hug", "Falcon"]
    plot_libs(df=occurrences_df, libraries=libraries, output_file=f"{args.path}{web_framework_libs.__name__}.pdf")


def postgres_drivers_libs(occurrences_df):
    libraries = ["sqlalchemy", "psycopg2_binary", "pg8000", "pygresql", "d6t", "psycopg2cffi"]
    plot_libs(df=occurrences_df, libraries=libraries, output_file=f"{args.path}{postgres_drivers_libs.__name__}.pdf")


# def database_driver_libs(occurrences_df):
#     libraries = ["sqlalchemy", "psycopg2", "pg8000", "pygresql", "d6t", "psycopg2cffi"]
#     plot_libs(df=occurrences_df, libraries=libraries, output_file=f"{args.path}{database_driver_libs.__name__}.pdf")

def main(args):
    occurrences_df = pd.read_csv(filepath_or_buffer=f"{args.path}library_count_all_threads.csv", header=0)

    topX(df=occurrences_df, X=60, output_file=f"{args.path}top{60}.pdf")

    # libraries = ['pandas', 'cudf', 'pyspark', 'spark', 'dask', 'arrow', 'duckdb', 'modin', 'polars', 'dplyr',
    #              'clickhouse_connect', 'datatable']
    # plot_libs(df=occurrences_df, libraries=libraries, output_file=f"{args.path}data_libraries.pdf")

    data_analysis_libs(occurrences_df)
    machine_learning_libs(occurrences_df)
    visualization_libs(occurrences_df)
    web_framework_libs(occurrences_df)
    postgres_drivers_libs(occurrences_df)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', help="The path to the library counts")
    args = parser.parse_args()

    main(args)
