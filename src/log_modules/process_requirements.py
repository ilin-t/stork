import os
import pandas as pd

from os.path import isfile, join
from collections import Counter

from matplotlib import pyplot as plt

# sc = SparkContext("local", "Requirements file parser")
# rdd = pyspark.SparkContext.

# packages_path = "/home/ilint/HPI/fs00/rabl/ilin.tolovski/stork/packages/"
# packages_path = "\\store-01.hpi.uni-potsdam.de\\fg\\rabl\\ilin.tolovski\\stork\\packages"
packages_path = r"//store-01.hpi.uni-potsdam.de/fg/rabl/ilin.tolovski/stork/packages/"

requirements_files = [f for f in os.listdir(packages_path) if isfile(join(packages_path, f))]
total_packages = {}
for requirements_file in requirements_files:
    packages_per_file = []
    with open(f"{packages_path}{requirements_file}", "r") as file:
        for line in file.readlines():
            package = line.split("==")[0]
            package = package.split("<")[0]
            package = package.split(">")[0]
            package = package.strip()
            packages_per_file.append(package)
    # print(f"{requirements_file}: {packages_per_file}")
    file.close()
    total_packages[requirements_file] = packages_per_file
    # total_packages.append({requirements_file:packages_per_file})
print(total_packages)

# extract packages

complete_list = []
#
for single_list in total_packages.values():
    for value in single_list:
        complete_list.append(value)

unique_packages = set(complete_list)
# print(unique_packages)

# count occurences:
occurences = Counter(complete_list)
with open("occurences.csv", "w") as file:
    file.write("library,count\n")
    for library, count in occurences.items():
        if library == "":
            continue
        file.write('{},{}\n'.format(str(library), str(count)))
file.close()
print(str(occurences.items()))

plt.bar(x=occurences.keys(), height=occurences.values())
plt.ylim(0, max(occurences.values()))
plt.show()
