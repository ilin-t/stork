
import pyspark
from pyspark import SparkContext
import os
from os.path import isfile, join

# sc = SparkContext("local", "Requirements file parser")
# rdd = pyspark.SparkContext.

packages_path = "/home/ilint/HPI/fs00/rabl/ilin.tolovski/stork/packages/"

requirements_files = [f for f in os.listdir(packages_path) if isfile(join(packages_path, f))]
total_packages = []
for requirements_file in requirements_files:
    packages_per_file = []
    with open(f"{packages_path}{requirements_file}", "r") as file:
        for line in file.readlines():
            package = line.split("==")[0]
            packages_per_file.append(package)
    print(f"{requirements_file}: {packages_per_file}")
    file.close()
    total_packages.append({requirements_file:packages_per_file})

