import sys
import time
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.sql import text
import logging

logging.basicConfig(filename='pd_to_sql_pipe.log', encoding='utf-8', level=logging.DEBUG)

engine = create_engine('postgresql+psycopg2://postgres:vers.2.1@localhost/tpch')

with engine.connect() as conn:
    start_co = time.time_ns()
    customer_orders = pd. \
        read_sql_query(text("SELECT * FROM customer INNER JOIN orders ON customer.c_custkey=orders.\"O_CUSTKEY\";"), conn)
    sql_co = time.time_ns() - start_co

    start_lo = time.time_ns()
    lineitem_orders = pd. \
        read_sql(text("SELECT * FROM lineitem INNER JOIN orders ON orders.\"O_ORDERKEY\"=lineitem.l_orderkey;"), conn)
    sql_lo = time.time_ns() - start_lo

    # start_co_double = time.time_ns()
    # customers_orders_double = pd. \
    #     read_sql(text("SELECT * FROM (SELECT * FROM customer) as c INNER JOIN (SELECT * FROM orders) as o \
    #                 ON c.c_custkey=o.\"O_CUSTKEY\""), conn)
    # sql_co_double = time.time_ns() - start_co_double
    #
    # start_lo_double = time.time_ns()
    # lineitem_orders_double = pd. \
    #     read_sql(text("SELECT * FROM (SELECT * FROM lineitem) as l INNER JOIN (SELECT * FROM orders) as o \
    #                 ON o.\"O_ORDERKEY\"=l.l_orderkey;"), conn)
    # sql_lo_double = time.time_ns() - start_lo_double

    lo_size = sys.getsizeof(lineitem_orders)
    co_size = sys.getsizeof(customer_orders)
    # lo_double_size = sys.getsizeof(lineitem_orders_double)
    # co_double_size = sys.getsizeof(customers_orders_double)

    logging.info(f"Joining customers and orders via SELECT * FROM customer INNER JOIN orders ON customer.c_custkey=orders.\"O_CUSTKEY\": {sql_co/1000000} ms.")
    logging.info(f"Joining lineitem and orders via SELECT * FROM lineitem INNER JOIN orders ON orders.\"O_ORDERKEY\"=lineitem.l_orderkey: {sql_lo/1000000} ms.")
    # logging.info(f"Joining customers and orders via SELECT * FROM (SELECT * FROM customer) INNER JOIN (SELECT * FROM orders) \
    #                 ON customer.c_custkey=orders.\"O_CUSTKEY\";: {sql_co_double/1000000} ms.")
    # logging.info(f"Joining lineitem and orders via SELECT * FROM (SELECT * FROM lineitem) INNER JOIN (SELECT * FROM orders) \
    #                 ON orders.\"O_ORDERKEY\"=lineitem.l_orderkey;: {sql_lo_double/1000000} ms.")

    logging.info(f"Size of joined lineitem and orders: {lo_size/1000000} MB.")
    # logging.info(f"Size of double joined lineitem and orders: {lo_double_size/1000000} MB.")
    logging.info(f"Size of joined customer and orders: {co_size/1000000} MB.")
    # logging.info(f"Size of double joined customer and orders: {co_double_size/1000000} MB.")


