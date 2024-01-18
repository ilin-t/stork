"""
Module Name: data_grapher

Description: This module provides functionality for easy data graphing.

Author: Sudo-Ivan
"""

import os
import sys
import argparse
import matplotlib.pyplot as plt
import pandas as pd

def plot_line_chart(data_file, x_column, y_column, title):
    """
    Plot a line chart using data from a file.

    Args:
        data_file (str): Path to the data file.
        x_column (str): Name of the column for x-axis values.
        y_column (str): Name of the column for y-axis values.
        title (str): Title of the line chart.

    Returns:
        None
    """
    data = pd.read_csv(data_file)
    plt.plot(data[x_column], data[y_column])
    plt.title(title)
    plt.xlabel(x_column)
    plt.ylabel(y_column)
    plt.show()

def plot_bar_chart(data_file, x_column, y_column, title):
    """
    Plot a bar chart using data from a file.

    Args:
        data_file (str): Path to the data file.
        x_column (str): Name of the column for x-axis values.
        y_column (str): Name of the column for y-axis values.
        title (str): Title of the bar chart.

    Returns:
        None
    """
    data = pd.read_csv(data_file)
    plt.bar(data[x_column], data[y_column])
    plt.title(title)
    plt.xlabel(x_column)
    plt.ylabel(y_column)
    plt.show()

def plot_scatter_chart(data_file, x_column, y_column, title):
    """
    Plot a scatter chart using data from a file.

    Args:
        data_file (str): Path to the data file.
        x_column (str): Name of the column for x-axis values.
        y_column (str): Name of the column for y-axis values.
        title (str): Title of the scatter chart.

    Returns:
        None
    """
    data = pd.read_csv(data_file)
    plt.scatter(data[x_column], data[y_column])
    plt.title(title)
    plt.xlabel(x_column)
    plt.ylabel(y_column)
    plt.show()

def main(args):
    """
    Main function to handle command-line arguments and call appropriate functions.

    Args:
        args (list): List of command-line arguments.

    Returns:
        None
    """
    parser = argparse.ArgumentParser(description="Easy data graphing.")
    parser.add_argument("chart_type", choices=["line", "bar", "scatter"], help="Type of graph to plot (line, bar, scatter).")
    parser.add_argument("data_file", type=str, help="Path to the data file.")
    parser.add_argument("x_column", type=str, help="Name of the column for x-axis values.")
    parser.add_argument("y_column", type=str, help="Name of the column for y-axis values.")
    parser.add_argument("title", type=str, help="Title of the chart.")
    parsed_args = parser.parse_args(args)

    if parsed_args.chart_type == "line":
        plot_line_chart(parsed_args.data_file, parsed_args.x_column, parsed_args.y_column, parsed_args.title)
    elif parsed_args.chart_type == "bar":
        plot_bar_chart(parsed_args.data_file, parsed_args.x_column, parsed_args.y_column, parsed_args.title)
    elif parsed_args.chart_type == "scatter":
        plot_scatter_chart(parsed_args.data_file, parsed_args.x_column, parsed_args.y_column, parsed_args.title)

if __name__ == "__main__":
    main(sys.argv[1:])