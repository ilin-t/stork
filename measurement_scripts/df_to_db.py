# measure the overhead that a dataframe creates when moved to the DB with to_sql
import sys
import memory_profiler
import numpy as np
import pandas as pd
import psycopg2
import logging
import time
import sqlalchemy
from matplotlib import pyplot as plt

from sqlalchemy import create_engine

engine = create_engine('postgresql+psycopg2://postgres:vers.2.1@localhost/tpch')


# Generate Line item scale factor 10: dbgen -s 10 -f -T L -v
# Generate Line item scale factor 1: dbgen -s 1 -f -T L -v

@memory_profiler.profile
def measure_read_time(filepath):
    start = time.time_ns()
    lineitem = pd.read_table(filepath, delimiter="|")
    read_time = time.time_ns() - start
    table_size = sys.getsizeof(lineitem)
    logging.info(f"Reading {filepath} in memory: {read_time / 1000000} ms.")
    logging.info(f"Size of {filepath} in memory: {table_size / 1000000} MB.")


def measure_df_to_db(filepath):
    columns = ["l_orderkey", "l_partkey", "l_suppkey", "l_linenumber",
               "l_quantity", "l_extendedprice", "l_discount", "l_tax", "l_returnflag",
               "l_linestatus", "l_shipdate", "l_commitdate", "l_receiptdate", "l_shipinstruct",
               "l_shipmode", "l_comment"]

    start = time.time_ns()
    lineitem = pd.read_table(filepath, header=0, names=columns, delimiter="|")
    read_time = time.time_ns() - start
    table_size = sys.getsizeof(lineitem)
    logging.info(f"Reading {filepath} in memory: {read_time / 1000000} ms.")
    logging.info(f"Size of {filepath} in memory: {table_size / 1000000} MB.")

    engine = create_engine('postgresql+psycopg2://postgres:vers.2.1@localhost/tpch')
    with engine.connect() as conn:
        start_to_sql = time.time_ns()
        lineitem.to_sql('lineitem10', schema='public', if_exists='replace', index=False, con=conn)
        send_time = time.time_ns() - start_to_sql
        # table_size = sys.getsizeof(lineitem)
        logging.info(f"Sending lineitem dataframe to Postgresql: {send_time / 1000000} ms.")


def plot_measurements():
    #     measurements = pd.DataFrame(columns=["framework", "resource", "value", "unit"],
    #                                 data=np.array([
    #                                     ["postgresql", "memory", 879, "MB"],
    #                                     ["panda", "memory", 3569, "MB"],
    #                                     ["native", "memory", 753, "MB"],
    #                                     ["panda", "time", 398.96, "s"],
    #                                     ["postgresql", "time", 14.38, "s"],
    #                                     ["postgresql_sf10", "time", 163.27, "s"]
    #                                 ]))
    #
    fig = plt.figure(figsize=(6, 5))
    plt.yticks(np.arange(0, 402, 100))
    bars = plt.bar(["pandas", "postgres"], [398.96, 14.98], color='maroon',
                   width=0.3)
    plt.ylabel("Data transfer time (s)")
    plt.bar_label(bars)
    plt.savefig("time_df_to_db.pdf", dpi='figure', format="pdf")

    fig = plt.figure(figsize=(6, 5))
    # plt.yscale("log")
    plt.yticks(np.arange(0, 4002, 1000))
    bars = plt.bar(["pandas", "postgres", "native"], [3569, 879, 753], color='maroon',
                   width=0.3)
    plt.bar_label(bars)
    plt.ylabel("Storage footprint (MB)")
    plt.savefig("memory_df_to_db.pdf", dpi='figure', format="pdf")


#                         {"framework": "pandas", "resource":"memory", "value": 3569, "unit":"MB"},
#                         {"framework": "native", "resource":"memory", "value": 753, "unit":"MB"},
#                         {"framework": "pandas", "resource": "time", "value": 398.96, "unit": "s"},
#                         {"framework": "postgresql", "resource": "time", "value": 14.38, "unit": "s"},

if __name__ == '__main__':
    logging.basicConfig(filename='df_to_db.log', encoding='utf-8', level=logging.DEBUG)
    # file_path = "/home/ilint/HPI/repos/tpch-data/lineitem_sf10.tbl"
    # # measure_read_time(filepath=file_path)
    # measure_df_to_db(file_path)
    #
    # columns = ["l_orderkey", "l_partkey", "l_suppkey", "l_linenumber",
    #            "l_quantity", "l_extendedprice", "l_discount", "l_tax", "l_returnflag",
    #            "l_linestatus", "l_shipdate", "l_commitdate", "l_receiptdate", "l_shipinstruct",
    #            "l_shipmode", "l_comment"]

    plot_measurements()
