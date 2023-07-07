# # measure the overhead of executing a dataframe operation on client -
# # vs executing the equivalent SQL statements on the DB
import logging
import sys
import numpy as np
from matplotlib import pyplot as plt

import pandas as pd
import time

filepath = "/home/ilint/HPI/repos/tpch-data/"

logging.basicConfig(filename='pd_to_sql.log', encoding='utf-8', level=logging.DEBUG)

lineitem_cols = ["l_orderkey", "l_partkey", "l_suppkey", "l_linenumber",
           "l_quantity", "l_extendedprice", "l_discount", "l_tax", "l_returnflag",
           "l_linestatus", "l_shipdate", "l_commitdate", "l_receiptdate", "l_shipinstruct",
           "l_shipmode", "l_comment"]

orders_cols = ["l_orderkey", "custkey", "orderstatus", "totalprice", "orderdate",
               "order_priority", "clerk", "ship_priority", "comment"]

customer_cols = ["custkey", "name", "address", "nationkey", "phone", "acctbal",
                 "mktsegment", "comment"]

start_lineitem = time.time_ns()
lineitem = pd.read_table(filepath + "lineitem_sf1.tbl", header=0, names=lineitem_cols, delimiter="|")
lineitem_read_time = time.time_ns() - start_lineitem

start_orders = time.time_ns()
orders = pd.read_table(filepath + "orders_sf1.tbl", header=0, names=orders_cols, delimiter="|")
orders_read_time = time.time_ns() - start_orders

start_customers = time.time_ns()
customers = pd.read_table(filepath + "customers_sf1.tbl", header=0, names=customer_cols, delimiter="|")
customers_read_time = time.time_ns() - start_customers

start_merge_lo = time.time_ns()
lineitem_orders = pd.merge(left=lineitem, right=orders, how="inner", on="l_orderkey")
merge_time_lo = time.time_ns() - start_merge_lo

start_merge_co = time.time_ns()
customers_orders = pd.merge(left=customers, right=orders, how="inner", on="custkey")
merge_time_co = time.time_ns() - start_merge_co

lineitem_size = sys.getsizeof(lineitem)
lineitem_orders_size = sys.getsizeof(lineitem_orders)
customers_size = sys.getsizeof(customers)
orders_size = sys.getsizeof(orders)
customers_orders_size = sys.getsizeof(customers_orders)


logging.info(f"Reading {filepath+'lineitem'} in memory: {lineitem_read_time / 1000000} ms.")
logging.info(f"Reading {filepath+'customers'} in memory: {customers_read_time / 1000000} ms.")
logging.info(f"Reading {filepath+'orders'} in memory: {orders_read_time / 1000000} ms.")


logging.info(f"Merging time for lineitem and orders: {merge_time_lo / 1000000} ms.")
logging.info(f"Merging time for customers and orders: {merge_time_co / 1000000} ms.")


logging.info(f"Size of {filepath+'lineitem'}: {lineitem_size / 1000000} MB.")
logging.info(f"Size of {filepath+'customers'}: {customers_size / 1000000} MB.")
logging.info(f"Size of {filepath+'orders'}: {orders_size / 1000000} MB.")


logging.info(f"Size of merged lineitem_orders: {lineitem_orders_size / 1000000} MB.")
logging.info(f"Size of merged customers_orders: {customers_orders_size / 1000000} MB.")




def plot_measurements():
    fig = plt.figure(figsize=(6, 5))
    plt.yticks(np.arange(0, 16, 1))

    # creating the bar plot
    bars = plt.bar(["pandas", "postgres"], [13.01, 12.47], color='maroon',
        width=0.3)

    plt.ylabel("Data transfer time (s)")

    plt.bar_label(bars)
    plt.savefig("time_lo.pdf", dpi='figure', format="pdf")

    fig = plt.figure(figsize=(6, 5))
    plt.yticks(np.arange(0, 6001, 1000))
    bars = plt.bar(["pandas", "postgres"], [5969, 1569], color='maroon',
            width=0.3)
    plt.bar_label(bars)
    plt.ylabel("Storage footprint (MB)")
    plt.savefig("memory_lo.pdf", dpi='figure', format="pdf")




