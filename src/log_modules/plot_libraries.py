import argparse
import math
import os
from math import ceil

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import pylab
import pandas as pd

plt.rcParams["axes.prop_cycle"] = plt.cycler('color',
                                             ['#66c2a5', '#fc8d62', '#8da0cb', '#e78ac3',
                                              '#a6d854', '#ffd92f', '#e5c494', '#b3b3b3'])

def addlabels(x, y):
    for i in range(0, len(x)):
        print(y.iloc[i])
        plt.text(x=i, y=y.iloc[i] + 5, s=y.iloc[i], ha="center")


def addlabels_array(x, y):
    for i in range(0, len(x)):
        # print(y.iloc[i])
        plt.text(x=i, y=y[i], s=y[i], ha="center")


def topX(df, X, output_file):
    df.sort_values(by="count", ascending=False, inplace=True)
    if X < len(df):
        subset = df.iloc[:X][:]
    else:
        subset = df
    try:
        if max(subset["count"]) == 0:
            return 0
        else:
            print(subset)
            plt.figure(figsize=(11, 5))
            plt.bar(x=subset["library"], height=subset["count"], width=0.8, align='center',
                    label="Usage of Python Packages across Repositories")
            addlabels(x=subset["library"], y=subset["count"])
            # plt.xlabel("Python Packages")
            plt.ylabel("# of Occurences")
            plt.ylim(0, max(subset["count"]) + 10)
            plt.xlim([-0.75, len(subset["library"]) - 0.25])
            plt.xticks(rotation=60)

            plt.yticks(range(0, (max(subset["count"]) + (max(subset["count"]) // 5)),
                             ((max(subset["count"]) + max(subset["count"]) // 10) // 5) + 1))
            plt.rcParams.update({'font.size': 18})
            plt.tight_layout()
            # plt.show()
            plt.savefig(fname=output_file, dpi=300, pad_inches=0)

    except ValueError as e:
        print(e)


def yearly_splits(years, nr_repos, output_file):
    plt.figure(figsize=(9, 4))
    plt.bar(x=years, height=nr_repos, width=0.8, align='center', label="Python Repositories (MIT)")
    addlabels_array(x=years, y=nr_repos)
    # plt.xlabel("Python Packages")
    plt.ylabel("# of Repositories (MIT)")
    plt.ylim(0, max(nr_repos) + 10)
    plt.xlim([-0.75, len(years) - 0.25])
    plt.xticks(rotation=60)

    plt.yticks(range(0, 125001, 25000))
    plt.rcParams.update({'font.size': 24})
    plt.tight_layout()
    # plt.show()
    plt.savefig(fname=output_file, dpi=300, pad_inches=0)


def library_per_year(library, year):
    df = pd.read_csv(f"../../analysis_results/yearly_splits/occurrences-{year}.csv")
    print(df[df['library'] == library]['count'].values)
    return df[df['library'] == library]['count'].values


def aggregate_counts_per_year(library, start_year, end_year):
    counts_years = {}
    for i in range(start_year, end_year + 1):
        counts_years[i] = library_per_year(library=library, year=i)

    # print(pd.DataFrame.from_dict(data=counts_years, orient='index', columns=['count']))
    # pd.DataFrame.from_dict(data=counts_years, orient='index', columns=['count']).to_csv(f"{library}_counts.csv")
    return pd.DataFrame.from_dict(data=counts_years, orient='index', columns=['count'])


def bar_plot_df(df, library, output_file):
    plt.figure(figsize=(10, 6))
    plt.bar(x=df.index.astype(str), height=df['count'], width=0.8, align='center',
            label=f"Yearly overview of {library}")
    addlabels_array(x=range(0, 6), y=df["count"].to_list())
    plt.xlabel(f"Yearly overview of {library}")
    plt.ylabel("# of Occurences")
    plt.ylim(0, (max(df["count"]) + max(df["count"]) / 10))
    plt.xlim([-0.75, len(df.index) - 0.25])
    plt.xticks(rotation=60)

    plt.yticks(range(0, (max(df["count"]) + (max(df["count"]) // 5)),
                     ((max(df["count"])) // 5)))
    plt.rcParams.update({'font.size': 20})
    plt.tight_layout()
    plt.savefig(fname=output_file, dpi=300, pad_inches=0)
    plt.close()

def plot_libs(df, libraries, output_file):
    lib_df = pd.DataFrame(columns=["library", "count"])
    for library in libraries:
        p = df[df["library"] == library]
        if p.empty:
            print(f"p is empty {p['library']}")
            # lib_df = lib_df.append(pd.DataFrame(data={'library': library, 'count': 0}, index=[0]), ignore_index=True)
            continue
        else:
            lib_df = lib_df.append(p, ignore_index=True)
    lib_df.sort_values(by="count", ascending=False, inplace=True)
    print(lib_df)

    topX(df=lib_df, X=len(lib_df), output_file=output_file)


def plot_data_analysis_libs(occurrences_df):
    libraries = ['numpy', 'pandas', 'cudf', 'pyspark', 'spark', 'dask', 'arrow', 'duckdb', 'modin', 'polars', 'dplyr',
                 'clickhouse', 'datatable']
    # libraries = ['numpy', 'pandas', 'cudf', 'pyspark', 'spark', 'dask', 'arrow', 'duckdb', 'modin', 'polars', 'dplyr',
    #              'clickhouse_connect', 'datatable']
    plot_libs(df=occurrences_df, libraries=libraries,
              output_file=f"{args.outputs}/plots/{plot_data_analysis_libs.__name__}.pdf")


def plot_machine_learning_libs(occurrences_df):
    libraries = ['scikit_learn', "torch", "torchvision", "torchaudio", "tensorflow", "tensorboard", "keras", 'theano']
    plot_libs(df=occurrences_df, libraries=libraries,
              output_file=f"{args.outputs}/plots/{plot_machine_learning_libs.__name__}.pdf")


def plot_visualization_libs(occurrences_df):
    libraries = ["matplotlib", "seaborn", "plotly", "ggplot", "bokeh"]
    plot_libs(df=occurrences_df, libraries=libraries,
              output_file=f"{args.outputs}/plots/{plot_visualization_libs.__name__}.pdf")


def plot_web_framework_libs(occurrences_df):
    libraries = ["Django", "Flask", "CherryPy", "Bottle", "Hug", "Falcon"]
    plot_libs(df=occurrences_df, libraries=libraries,
              output_file=f"{args.outputs}/plots/{plot_web_framework_libs.__name__}.pdf")


def plot_postgres_drivers_libs(occurrences_df):
    libraries = ["sqlalchemy", "psycopg2_binary", "asyncpg", "aiopg", "pgzero", "pglast", "", "pg8000", "pygresql",
                 "d6t", "psycopg2cffi"]
    plot_libs(df=occurrences_df, libraries=libraries,
              output_file=f"{args.outputs}/plots/{plot_postgres_drivers_libs.__name__}.pdf")


def get_mysql_drivers_libs():
    libraries = ['pymysql', 'mysql_connector_repackaged', 'MySQL-python', 'aiomysql', 'django_mysql', 'mysqlclient']
    return libraries


def get_postgres_drivers_libs():
    libraries = ["sqlalchemy", "psycopg2_binary", "asyncpg", "aiopg", "pgzero", "pglast", "", "pg8000", "pygresql",
                 "d6t", "psycopg2cffi"]
    return libraries


def get_sqlite_drivers_libs():
    libraries = ["sqlite3", "pysqlite"]
    return libraries


def get_mongodb_libs():
    libraries = ['pymongo', 'mongoengine', 'flask_mongoengine', 'umongo', 'mongomock', 'flask_pymongo',
                 'extras_mongoengine', 'django_mongoengine']
    return libraries


def get_sqlalchemy_libs():
    libraries = ['SQLAlchemy', 'flask_sqlalchemy', 'graphene_sqlalchemy', 'marshmallow_sqlalchemy', 'sqlalchemy_mptt',
                 'sqlalchemy_aio']
    return libraries


def count_occurrences(libraries, occurrences_df):
    count = 0
    for lib in libraries:
        try:
            print(f"Library: {lib_occurence}")
            if lib_occurence.lower() in lib.lower():
                temp = occurrences_df.loc[occurrences_df["library"] == lib_occurence, "count"]
                print(f"Library: {lib_occurence} found in {lib}. Count: {temp}")
                if temp.values.size > 0:
                    count += temp.values[0]
        except KeyError as e:
            print(f"Library {lib} not found in occurrences list.")
    return count


def aggregate_db_libs(occurrences_df):
    mongo_libs = get_mongodb_libs()
    pg_libs = get_postgres_drivers_libs()
    mysql_libs = get_mysql_drivers_libs()
    sqlite_libs = get_mysql_drivers_libs()
    sqlalchemy_libs = get_sqlalchemy_libs()

    count_mongo = count_occurrences(mongo_libs, occurrences_df)
    count_pg = count_occurrences(pg_libs, occurrences_df)
    count_mysql = count_occurrences(mysql_libs, occurrences_df)
    count_sqlite = count_occurrences(sqlite_libs, occurrences_df)
    count_sqlalchemy = count_occurrences(sqlalchemy_libs, occurrences_df)

    df = pd.DataFrame.from_dict(data={"library": ["Postgres", "MongoDB", "MySQL", "SQLite", "SQLAlchemy"],
                                      "count": [count_pg, count_mongo, count_mysql, count_sqlite, count_sqlalchemy]})
    print(df)
    return df


def plot_db_libs(occurrences_df):
    df_db_libs = aggregate_db_libs(occurrences_df)
    plot_libs(df=df_db_libs, libraries=df_db_libs["library"].values,
              output_file=f"{args.outputs}/plots/{plot_db_libs.__name__}.pdf")

def plot_lines_df(df_list, libs, libgroup):
    max_values = []
    colors = pylab.cm.cbook
    plt.figure(figsize=(10, 6))

    for i in range(0, len(df_list)):
        plt.plot(df_list[i].index.astype(str), df_list[i]['count'], marker='o', label=libs[i])
        # addlabels_array(x=range(0, len(df_list[i].index)), y=df_list[i]['count'].to_list())
        max_values.append(max(df_list[i]['count']))
    plt.xlabel(f"Yearly overview of DM libraries")
    plt.ylabel("# of Occurences")
    plt.ylim(0, max(max_values) + max(max_values) / 10)
    plt.xlim([-0.75, len(df_list[0].index) - 0.25])
    plt.xticks(rotation=60)

    plt.legend()

    plt.yticks(np.linspace(0, max(max_values), 5))
    plt.rcParams.update({'font.size': 20, 'image.cmap': 'Pastel2'})
    plt.tight_layout()
    plt.savefig(fname=f'{libgroup}.png', dpi=300, pad_inches=0)
    plt.close()

# def database_driver_libs(occurrences_df):
#     libraries = ["sqlalchemy", "psycopg2", "pg8000", "pygresql", "d6t", "psycopg2cffi"]
#     plot_libs(df=occurrences_df, libraries=libraries, output_file=f"{args.path}{database_driver_libs.__name__}.pdf")

def main(args):
    os.makedirs(f"{args.outputs}/plots/", exist_ok=True)
    # occurrences_df = pd.read_csv(filepath_or_buffer=f"{args.outputs}/occurrences/library_count_all_threads.csv",
    #                              header=0)

    # topX(df=occurrences_df, X=20, output_file=f"{args.outputs}/plots/top{20}.svg")
    occurrences_df = pd.read_csv("../../analysis_results/yearly_splits/occurences_summed.csv")
    # topX(df=occurrences_df, X=20, output_file="../../analysis_results/plots/top20.png")
    # plot_data_analysis_libs(occurrences_df)
    # plot_machine_learning_libs(occurrences_df)
    # plot_visualization_libs(occurrences_df)
    # plot_web_framework_libs(occurrences_df)
    # plot_postgres_drivers_libs(occurrences_df)
    # plot_db_libs(occurrences_df)

    years = ['2018', '2019', '2020', '2021', '2022', '2023']
    nr_repos = [65648, 65440, 54924, 115288, 107436, 85785]

    aggregate_db_libs(occurrences_df=occurrences_df)

    # yearly_splits(years = years, nr_repos = nr_repos, output_file= "python_repos.pdf")
    # yearly_splits(years = years, nr_repos = nr_repos, output_file= "python_repos.svg")
    # yearly_splits(years = years, nr_repos = nr_repos, output_file="../../analysis_results/plots/python_repos.png")

    # library_per_year('numpy', 2018)

    dm_libs = ['numpy', 'pandas', 'scipy', 'sqlalchemy']
    ml_libs = ['sklearn', 'tensorflow', 'keras', 'torch']

    # numpy_counts = aggregate_counts_per_year(library='numpy', start_year=2018, end_year=2023)
    # sklearn_counts = aggregate_counts_per_year(library='scikit_learn', start_year=2018, end_year=2023)
    # pandas_counts = aggregate_counts_per_year(library='pandas', start_year=2018, end_year=2023)
    # scipy_counts = aggregate_counts_per_year(library='scipy', start_year=2018, end_year=2023)
    # tf_counts = aggregate_counts_per_year(library='tensorflow', start_year=2018, end_year=2023)
    # sqlalchemy_counts = aggregate_counts_per_year(library='SQLAlchemy', start_year=2018, end_year=2023)
    # keras_counts = aggregate_counts_per_year(library='keras', start_year=2018, end_year=2023)
    # torchvision_counts = aggregate_counts_per_year(library='torchvision', start_year=2018, end_year=2023)
    # torch_counts = aggregate_counts_per_year(library='torch', start_year=2018, end_year=2023)

    # plot_lines_df([numpy_counts, pandas_counts, scipy_counts, sqlalchemy_counts], dm_libs, libgroup='dm_libs')
    # plot_lines_df([sklearn_counts, tf_counts, keras_counts, torch_counts], ml_libs, libgroup='ml_libs')




    # bar_plot_df(df=numpy_counts, library='numpy', output_file='numpy_yearly_18_23.png')
    # bar_plot_df(df=pandas_counts, library='pandas', output_file='pandas_yearly_18_23.png')
    # bar_plot_df(df=torch_counts, library='torch', output_file='torch_yearly_18_23.png')
    # bar_plot_df(df=scipy_counts, library='scipy', output_file='scipy_yearly_18_23.png')
    # bar_plot_df(df=sklearn_counts, library='scikit_learn', output_file='sklearn_yearly_18_23.png')
    # bar_plot_df(df=tf_counts, library='tensorflow', output_file='tf_yearly_18_23.png')
    # bar_plot_df(df=torchvision_counts, library='torchvision', output_file='torchvision_yearly_18_23.png')
    # bar_plot_df(df=sqlalchemy_counts, library='SQLAlchemy', output_file='sqlalchemy_yearly_18_23.png')
    # bar_plot_df(df=keras_counts, library='keras', output_file='../../analysis_results/plots/keras_yearly_18_23.png')
    # yearly_splits(years=numpy_counts.index, nr_repos=numpy_counts['count'].values, output_file='numpy_yearly_18_23_1.png')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--outputs', help="The path to the library counts")
    args = parser.parse_args()

    main(args)
