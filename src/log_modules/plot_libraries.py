import argparse
import os
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
        plt.figure(figsize=(9, 4))
        plt.bar(x=subset["library"], height=subset["count"], width=0.8, align='center',
                label="Usage of Python Packages across Repositories")
        addlabels(x=subset["library"], y=subset["count"])
        # plt.xlabel("Python Packages")
        plt.ylabel("# of Occurences")
        plt.ylim(0, max(subset["count"]) + 10)
        plt.xlim([-0.75, len(subset["library"])-0.25])
        plt.xticks(rotation=60)

        plt.yticks(range(0, (max(subset["count"]) + (max(subset["count"]) // 5)),
                         ((max(subset["count"]) + max(subset["count"]) // 10) // 5) + 1))
        plt.rcParams.update({'font.size': 24})
        plt.tight_layout()
        # plt.show()
        plt.savefig(fname=output_file, dpi=300, pad_inches=0)


# def topX(df, X, output_file):
#     df.sort_values(by="count", ascending=False, inplace=True)
#     if X < len(df):
#         subset = df.iloc[:X][:]
#     else:
#         subset = df
#     if max(subset["count"]) == 0:
#         return 0
#     else:
#         print(subset)
#         plt.figure(figsize=(9, 7))
#         plt.bar(x=subset["library"], height=subset["count"], width=0.8, align='center',
#                 label="Usage of Python Packages across Repositories")
#         addlabels(x=subset["library"], y=subset["count"])
#         plt.xlabel("Python Packages")
#         plt.ylabel("# of Occurences")
#         plt.ylim(0, max(subset["count"]) + 10)
#         plt.xlim([-0.75, len(subset["library"])-0.25])
#         plt.xticks(rotation=60)
#
#         plt.yticks(range(0, (max(subset["count"]) + (max(subset["count"]) // 5)),
#                          ((max(subset["count"]) + max(subset["count"]) // 10) // 5) + 1))
#         plt.rcParams.update({'font.size': 24})
#         plt.tight_layout()
#         # plt.show()
#         plt.savefig(fname=output_file, dpi=300, pad_inches=0.1)

# def topX(df, X, output_file):
#     df.sort_values(by="count", ascending=False, inplace=True)
#     if X < len(df):
#         subset = df.iloc[:X][:]
#     else:
#         subset = df
#     if max(subset["count"]) == 0:
#         return 0
#     else:
#         print(subset)
#         plt.figure(figsize=(5, 3))
#         plt.bar(x=subset["library"], height=subset["count"], width=0.8, align='center',
#                 label="Usage of Python Packages across Repositories")
#         addlabels(x=subset["library"], y=subset["count"])
#         plt.xlabel("Python Packages")
#         plt.ylabel("# of Occurences")
#         plt.ylim(0, max(subset["count"]) + 10)
#         plt.xlim([-0.75, len(subset["library"])-0.25])
#         plt.xticks(rotation=60)
#
#         plt.yticks(range(0, (max(subset["count"]) + (max(subset["count"]) // 5)),
#                          ((max(subset["count"]) + max(subset["count"]) // 10) // 5) + 1))
#         plt.rcParams.update({'font.size': 24})
#         plt.tight_layout()
#         # plt.show()
#         plt.savefig(fname=output_file, dpi=300, pad_inches=0.1)

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
            temp = occurrences_df.loc[occurrences_df["library"] == lib, "count"]
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


# def database_driver_libs(occurrences_df):
#     libraries = ["sqlalchemy", "psycopg2", "pg8000", "pygresql", "d6t", "psycopg2cffi"]
#     plot_libs(df=occurrences_df, libraries=libraries, output_file=f"{args.path}{database_driver_libs.__name__}.pdf")

def main(args):
    os.makedirs(f"{args.outputs}/plots/", exist_ok=True)
    occurrences_df = pd.read_csv(filepath_or_buffer=f"{args.outputs}/occurrences/library_count_all_threads.csv",
                                 header=0)

    topX(df=occurrences_df, X=20, output_file=f"{args.outputs}/plots/top{20}.svg")
    # plot_data_analysis_libs(occurrences_df)
    # plot_machine_learning_libs(occurrences_df)
    # plot_visualization_libs(occurrences_df)
    # plot_web_framework_libs(occurrences_df)
    # plot_postgres_drivers_libs(occurrences_df)
    # plot_db_libs(occurrences_df)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--outputs', help="The path to the library counts")
    args = parser.parse_args()

    main(args)
